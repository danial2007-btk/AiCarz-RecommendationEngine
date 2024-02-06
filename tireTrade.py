from keras.models import load_model
import numpy as np
from keras.preprocessing import image
from io import BytesIO

# Load your pre-trained model
model = load_model('tyre.h5')

def preprocess_image(contents):
    try:
        # Convert the image file to a numpy array
        img = image.load_img(BytesIO(contents), target_size=(224, 300))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0
        return img_array
    except Exception as e:
        raise ValueError(str(e))

def predict_image(img_array):
    # Make a prediction
    predictions = model.predict(img_array)
    predicted_class = 1 if predictions[0] > 0.5 else 0
    return "Good" if predicted_class == 1 else "Defected"
