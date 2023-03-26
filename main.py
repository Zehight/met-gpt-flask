import json
import time
from flask import Flask, request, render_template, jsonify
import os
import requests
import ffmpeg
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def trans_to_wav(file):
    file_path = os.path.join(file.filename)
    try:
        new_file_path = os.path.join('audio_' + file.filename.rsplit('.', 1)[0] + '.wav')
        file.save(file_path)
        input_file = ffmpeg.input(file_path)
        output_file = input_file.filter('atempo', tempo=1.5).output(new_file_path, codec='libmp3lame', ac=1, ar='16k',format='mp3')
        ffmpeg.run(output_file, overwrite_output=True)
    except Exception as e:
        os.remove(file_path)
        raise e
    finally:
        os.remove(file_path)
    return new_file_path


def chat(audio_path):
    try:
        with open(audio_path, "rb") as audio_file:
            audioResponse = json.loads(requests.post('https://api.miragari.com/fast/wavToText', files={'file': audio_file}).text)
    except Exception as e:
        # 出现异常时删除文件
        os.remove(audio_path)
        # 重新抛出异常
        raise e
    finally:
        # 无论是否出现异常，都执行删除文件操作
        os.remove(audio_path)
    all_speak = audioResponse['text'].split(' ')
    all_speak_string = '以下是一段音频内容，请详细的说它所讲的内容：' + ",".join(all_speak)
    user_question = {'role': 'user', 'content': all_speak_string}
    token_num = requests.post('https://api.miragari.com/fast/getTokenNum', json={'question': [user_question]}).text
    if(int(token_num)> 4000):
        final_res = {'role': 'bot',
                     'content': f'{token_num},超出限制'}
        return {'final_res': final_res, 'all_speak': all_speak}
    response = json.loads(requests.post('https://api.miragari.com/fast/fastChat', json={'question': [user_question]}).text)
    final_res = {'role': response['choices'][0]['message']['role'],
                 'content': response['choices'][0]['message']['content']}
    return {'final_res': final_res, 'all_speak': all_speak}


@app.route('/', methods=['GET'])
def index():
    return '欢迎'

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    audio_path = trans_to_wav(file)
    res = chat(audio_path)
    return {'finalRes': res['final_res'], 'allSpeak': res['all_speak']}


if __name__ == '__main__':
   app.run(debug=True)
