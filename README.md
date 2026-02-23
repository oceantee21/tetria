# Tetria

Simple Tetris clone in Python.

## Overview
Tetria — простая реализация игры Tetris на Python. Цель — управлять падающими фигурами, составлять полные линии и набирать очки.

## Features
- Movement, rotation, line clear
- Score and level progression
- Keyboard controls
- Optional assets folder for sprites/sounds

## Requirements
- Python 3.8+
- pygame (если используете): `pygame>=2.1.0`

## Installation
1. Клонируйте репозиторий:
   ```
   git clone https://github.com/oceantee21/tetria.git
   cd tetria
   ```
2. (Опционально) Создайте виртуальное окружение:
   ```
   python -m venv venv
   source venv/bin/activate   # macOS / Linux
   venv\Scripts\activate      # Windows
   ```
3. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```

## Run
```
python tetris.py
```

## Controls
- Left / Right — move piece  
- Up / X / Space — rotate  
- Down / S — soft drop  
- Space / Down — hard drop (если реализовано)  
- P — pause

(Отредактируйте, если в вашем коде другие клавиши.)

## Assets
Поместите изображения/звуки в папку `assets/`. Убедитесь, что все включённые ресурсы имеют лицензию, разрешающую распространение.

## Contributing
PRs и issues приветствуются. Пожалуйста, опишите изменения и добавьте инструкции для тестирования.

## License
This project is licensed under the MIT License — see the LICENSE file for details.

## Author
oceantee21 — https://github.com/oceantee21  
Email: killer999331@gmail.com
