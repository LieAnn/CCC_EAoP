
EAoP-Visualization
======================

# 1. virtualenv설치
	$ pip install virtualenv
	$ virtualenv venv

# 2. virtualenv 환경 구축
먼저 virtualenv 환경을 시행합니다.

	$ source venv/bin/activate

이후 requirements.txt 에 있는 모든 항목들을 설치합니다

	$ pip install -r requirements.txt

# 3. Flask 실행
	$ cd pyflask
	$ python app.py


# 4. Visualization 실행화면

첫 화면은 다음과 같습니다.
![index](./images/index.png)

아래와 같은 화면을 얻기 위해서는 컴퓨터 환경에 설치된 mysql DB위에 데이터를 util/_tsv2mysql.py 파일을 이용하여 넣어야합니다.

![post_vector](./images/post_vector.png)
![user_vector](./images/user_vector.png)


