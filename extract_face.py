import pymysql
import cv2

#from fastai.vision.all import *
import os
import numpy as np
from datetime import datetime


def label_func(o):
    return float(Path(o).parent.name)



def get_all_images_from_user(username):
    sql = f'select * from faces_new '



def check_image(image_id):

    sql = f'select * from '


class beauty_score(object):

    def __init__(self):
                
        # connect to db
        self.mydb = pymysql.connect(
            host="34.89.55.66",
            user="root",
            password="Mintylucky9",
            database="instagram",
            cursorclass=pymysql.cursors.DictCursor
        )

        self.mycursor = self.mydb.cursor()

        # load model
        #self.ML_model = load_learner('export.pkl')

        # Needed for image preprocessing later.
        self.CASCADE = "Face_cascade.xml"
        self.FACE_CASCADE = cv2.CascadeClassifier(self.CASCADE)


    # this is the main function for the class
    def images(self, username):
        image_count = 0

        # verify folder structure exists
        folder_checks(username)

        # list images that need to be processed
        images = os.listdir(f'instagram_webserver/static/images/{username}/process')

        # process each image
        for image in images:
            # extract faces from image
            processed_images = self.process_image(f'instagram_webserver/static/images/{username}/process/{image}')
            
            # move image from processed folder to finished folder
            os.system(f'mv images/{username}/process/{image} images/{username}/finish/{image}')

            # get ratings for the faces
            ratings = self.process_faces(processed_images, username, image_count)
            image_count += 1


    # Define function to extract and preprocess face images from photos. Results in 350x350 pixel images.
    def extract_faces(self, image):
        
        processed_images = []

        # convert image to grayscale
        image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Minimum size of detected faces is set to 75x75 pixels.
        faces = self.FACE_CASCADE.detectMultiScale(image_grey,scaleFactor=1.16,minNeighbors=5,minSize=(75,75),flags=0)

        for x,y,w,h in faces:
            # attempt to extract faces from each image
            try:
                sub_img = image[y-15:y+h+15,x-15:x+w+15]
                side = np.max(np.array([sub_img.shape[0],sub_img.shape[1]]))
                sub_image_padded = cv2.copyMakeBorder(sub_img,int(np.floor((side-sub_img.shape[1])/2)),int(np.ceil((side-sub_img.shape[1])/2)),int(np.floor((side-sub_img.shape[0])/2)),int(np.ceil((side-sub_img.shape[0])/2)),cv2.BORDER_CONSTANT)
                sub_image_resized = cv2.resize(src = sub_image_padded,dsize=(400,400))
                processed_images.append(sub_image_resized)
            except Exception as e:
                print(e)

        return processed_images


    # process each image
    def process_image(self, image_filename):

        # read the filename
        image = cv2.imread(image_filename)

        # get faces from image
        processed_images = self.extract_faces(image)

        return processed_images


    # get beauty score for each face
    def process_faces(self, processed_images, username, photo_num):

        face_count = 0
        ratings = [0]

        # iterate through processed_images
        # load the image and run it through the ML model
        if (len(processed_images) > 0):
            for face in processed_images:
                # get current time and date
                dt = self.get_dt()
                date_dt = dt[0]
                time_dt = dt[1]
                
                # write the face to a file
                filename = f"images/{username}/face/{photo_num}_{date_dt}_{time_dt}_{face_count}.jpg"

                cv2.imwrite(filename, face)

                # Apply the neural network to predict face beauty.
                pred = self.ML_model.predict(filename)

                # insert the face and rating into DB
                self.insert_face(username, pred[0][0], date_dt, time_dt, photo_num, filename)

                face_count += 1

        return ratings


    def update_ml_score(self, prediction, url):
        sql = f'''UPDATE faces SET score="{prediction}" WHERE url="{url}"'''
        self.mycursor.execute(sql)
        

    def commit_changes(self):
        self.mydb.commit()

    # not relevant either
    def get_faces(self):
        sql = '''SELECT url FROM faces WHERE score IS NULL'''
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())
        return results


    # not relevant now
    def predict_face(self, url):

        # Apply the neural network to predict face beauty.
        pred = self.ML_model.predict(url)
        return (pred[0][0])


    # get current time and date
    def get_dt(self):
        today = datetime.now()
        d1 = today.strftime("%d-%m-%Y")
        t1 = today.strftime("%H:%M:%S")

        return [d1, t1]

    
    # insert face into table
    def insert_face(self, username, score, date, time, photo_id, url):
        sql = f'''INSERT INTO faces_new (username, score, date, time, photo_id, url) VALUES ("{username}", "{score}", "{date}", "{time}", "{photo_id}", "{url}")'''
        self.mycursor.execute(sql)
        self.mydb.commit()



    # get list of images that haven't had the face extracted yet
    def get_images(self):
        sql = f'select * from images_new where faces_extracted is null'

        self.mycursor.execute(sql)

        results = list(self.mycursor.fetchall())

        return results



    def update_images_table_face_extracted(self, id):
        sql = f'UPDATE images_new SET faces_extracted="yes" WHERE id={id}'

        self.mycursor.execute(sql)
        self.mydb.commit()


    def enter_face(self, username, score, taken_at, photo_id, url, time_entered, date_entered, filename):
        sql = f'INSERT INTO faces_new (username, score, taken_at, photo_id, url, time_entered, date_entered, filename) VALUES ("{username}", {score}, "{taken_at}", "{photo_id}", "{url}", "{time_entered}", "{date_entered}", "{filename}")'

        self.mycursor.execute(sql)
        self.mydb.commit()

        return True


b = beauty_score()

images = b.get_images()

for image in images:
    username = image['username']
    filename = image['filename']

    table_id = image['id']
    faces = b.process_image(f'instagram_webserver/static/{filename}')

    face_count = 1
    for face in faces:
        photo_id = image['photo_id']

        root = 'instagram_webserver/static/'
        face_filename = f'images/{username}/face/{face_count}_{photo_id}.jpg'

        cv2.imwrite(f'{root}{face_filename}', face)

        score = -1.0
        date_entered, time_entered = b.get_dt()
        url = image['url']
        taken_at = image['taken_at']

        if (b.enter_face(username, score, taken_at, photo_id, url, time_entered, date_entered, face_filename)):
            pass
        else:
            print('Error saving photo in database')

        face_count += 1

    b.update_images_table_face_extracted(table_id)



