# -*- coding: utf-8 -*-#
# Author:       weiz
# Date:         2019/9/16 14:12
# Name:         flask_yolo
# Description: 一个可以在浏览器使用YOLO目标检测的函数，和一个可以通过网络访问的YOLO目标检测的接口
#              直接运行就可以在浏览器上面输入带检测图片，并返回检测的结果；同时，可以接受通过局域网
#              访问该接口的服务。

import base64
import json
import os
from datetime import timedelta
from io import BytesIO

import numpy as np
from PIL import Image
from flask import Flask, render_template, request, jsonify, make_response
from werkzeug.utils import secure_filename

import yolo.detect as detect

# 设置允许的文件格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'JPG', 'PNG', 'bmp'}
# i is pu


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


app = Flask(__name__)
# 设置静态文件缓存过期时间
app.send_file_max_age_default = timedelta(seconds = 1)


# @app.route('/upload', methods=['POST', 'GET'])
@app.route('/upload', methods = ['POST', 'GET'])  # 添加路由
def upload():
	print(request)
	if request.method == 'POST':
		f = request.files['file']

		if not (f and allowed_file(f.filename)):
			return jsonify({"state": False, "msg": "请检查上传的图片类型，仅限于png、PNG、jpg、JPG、bmp"})

		user_input = request.form.get("name")
		print(user_input)

		base_path = os.path.dirname(__file__)

		upload_path = os.path.join(base_path, 'static/images', secure_filename(f.filename))
		f.save(upload_path)

		loc = detect.run(source = upload_path)
		print(loc)
		print(os.listdir(loc))
		img_list = os.listdir(loc)
		for num in range(0, len(img_list)):
			img_name = img_list[num]
			img_list[num] = "data:image/" + img_name.split(".")[1] + ";base64," + \
							str(base64.b64encode(open(os.path.join(loc, img_name), "rb").read()))[2:][:-1]
			print(img_list[num])

		return jsonify({"state": True, "imgs": img_list})
	# return render_template('upload_ok.html', userinput = user_input, val1 = time.time(), data_dict = lab)

	return render_template('upload.html')


@app.route('/yolo_service', methods = ['POST'])
def detection():
	img = request.stream.read()
	f = BytesIO(img)
	image = Image.open(f)
	image = np.array(image, dtype = 'float32')
	boxes, lab = detect.run('yolov5s.pt', image)

	rsp = make_response(json.dumps(lab))
	rsp.mimetype = 'application/json'
	rsp.headers['Connection'] = 'close'
	return rsp


if __name__ == '__main__':
	app.run(host = '0.0.0.0', port = 5000)
