from flask import Flask, jsonify, request, render_template
from datetime import datetime
import json
import os
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
SAVE_DIR = 'saves'


class WebPet:
    def __init__(self, name):
        self.id = str(uuid.uuid4())
        self.name = name
        self.pressure = 30
        self.hunger = 40
        self.happiness = 60
        self.health = 90
        self.todos = []
        self.last_update = datetime.now().isoformat()
        self.survival_days = 0
        self.is_alive = True

    def to_dict(self):
        return vars(self)

    def update_stats(self):
        now = datetime.now()
        time_diff = (now - datetime.fromisoformat(self.last_update)).total_seconds()

        # 压力自动增长
        self.pressure = min(self.pressure + 0.5 * (time_diff / 60), 100)
        # 饥饿度增加
        self.hunger = min(self.hunger + 0.3 * (time_diff / 60), 100)
        # 更新最后更新时间
        self.last_update = now.isoformat()

        # 检查生存状态
        if self.pressure >= 100 or self.health <= 0:
            self.is_alive = False


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/game', methods=['POST'])
def handle_game():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        action = data.get('action', 'update')

        # 加载或创建新游戏
        if session_id and os.path.exists(f"{SAVE_DIR}/{session_id}.json"):
            with open(f"{SAVE_DIR}/{session_id}.json") as f:
                pet_data = json.load(f)
                pet = WebPet(pet_data['name'])
                pet.__dict__.update(pet_data)
        else:
            pet = WebPet("金璇")
            session_id = pet.id

        # 处理游戏逻辑
        if action == 'eat_takeout':
            pet.hunger = max(0, pet.hunger - 25)
            pet.pressure = min(100, pet.pressure + 5)
        elif action == 'rush_deadline':
            pet.pressure = max(0, pet.pressure - (30 if random.random() < 0.7 else -20))
            pet.health = max(0, pet.health - (0 if random.random() < 0.7 else 10))
        elif action == 'pretend_work':
            pet.pressure = max(0, pet.pressure - 15)
            pet.happiness = max(0, pet.happiness - 10)

        pet.update_stats()
        save_game(pet)

        return jsonify({
            "status": "success",
            "session_id": session_id,
            "data": pet.to_dict()
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


def save_game(pet):
    os.makedirs(SAVE_DIR, exist_ok=True)
    with open(f"{SAVE_DIR}/{pet.id}.json", 'w') as f:
        json.dump(pet.to_dict(), f, default=str)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)