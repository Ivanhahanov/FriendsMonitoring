from flask import Flask, make_response
import yaml
from pydantic import BaseModel
from vk_api import vk_api


class Settings:
    APP_ID: int
    SERVICE_TOKEN: str
    USER_ID: int


class OnlineUser(BaseModel):
    first_name: str
    last_name: str
    id: int
    online: int

    def to_metrics(self):
        name = f'{self.first_name}_{self.last_name}'.replace(' ', '')
        return f'{name} {self.online}'


class Config(Settings):
    def __init__(self, cfg_path):
        with open(cfg_path, 'r') as f:
            self._config = yaml.safe_load(f)

    def __getattribute__(self, item):
        cfg = super().__getattribute__('_config')
        if item.lower() in cfg:
            return cfg[item.lower()]
        else:
            return super().__getattribute__(item)


def load_config(filename) -> Config:
    return Config(filename)


app = Flask(__name__)
settings = load_config('settings.yml')


@app.route('/metrics')
def online_users():
    vk = vk_api.VkApi(app_id=settings.APP_ID, token=settings.SERVICE_TOKEN).get_api()
    users = vk.friends.get(user_id=settings.USER_ID, fields='online')
    metrics = [OnlineUser(**user).to_metrics() for user in users.get('items')]
    response = make_response('\n'.join(metrics), 200)
    response.mimetype = "text/plain"
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0')
