# -*- coding: utf-8 -*-#

import base64
import os
import uuid
from datetime import timedelta

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

import yolo.detect as detect

# 设置允许的文件格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'bmp'}


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
# 设置静态文件缓存过期时间
app.send_file_max_age_default = timedelta(seconds = 1)


@app.route('/upload', methods = ['POST', 'GET'])  # 添加路由
def upload():
	print(request)
	if request.method == 'POST':
		f = request.files['file']

		if not (f and allowed_file(f.filename)):
			return jsonify({"state": False, "msg": "请检查上传的图片类型，仅限于PNG、JPG、BMP。"})

		session_id = str(uuid.uuid4())
		# session_id = str(uuid.uuid5(uuid.NAMESPACE_OID, hashlib.md5(f)))

		base_path = os.path.dirname(__file__)

		upload_path = os.path.join(base_path, 'static/images',
		                           secure_filename(session_id + "." + f.filename.split(".")[1]))
		f.save(upload_path)

		loc = detect.run(source = upload_path, name = session_id)
		print(loc)
		print(os.listdir(loc))
		img_list = os.listdir(loc)
		for num in range(0, len(img_list)):
			img_name = img_list[num]
			img_list[num] = "data:image/" + img_name.split(".")[1] + ";base64," + \
			                str(base64.b64encode(open(os.path.join(loc, img_name), "rb").read()))[2:][:-1]
		# print(img_list[num])

		os.remove(upload_path)
		shutil.rmtree(loc)
		return jsonify({"state": True, "imgs": img_list})
	# return render_template('upload_ok.html', userinput = user_input, val1 = time.time(), data_dict = lab)

	return render_template('upload.html')


if __name__ == '__main__':
	app.run(host = '0.0.0.0', port = 5000)
