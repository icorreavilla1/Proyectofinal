import paho.mqtt.client as paho
import time
import streamlit as st
import cv2
import numpy as np
from PIL import Image
from keras.models import load_model

def on_publish(client, userdata, result):
    print("El dato ha sido publicado\n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

st.title("Feelify: Your Mood, Your Music 🎶")
st.subheader("Analizando tu estado de ánimo para ofrecerte la música perfecta")

broker = "broker.hivemq.com"
port = 1883
client1 = paho.Client("APP_CERR")
client1.on_message = on_message
client1.on_publish = on_publish
client1.connect(broker, port)

model = load_model('keras_model.h5')
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

img_file_buffer = st.camera_input("Toma una Foto")

if img_file_buffer is not None:
    img = Image.open(img_file_buffer)
    img = img.resize((224, 224))
    img_array = np.array(img)

    normalized_image_array = (img_array.astype(np.float32) / 127.0) - 1
    data[0] = normalized_image_array

    # Ejecuta la predicción
    prediction = model.predict(data)
    print(prediction)

    # Verificamos que st.session_state tenga un estado anterior registrado
    if "estado_anterior" not in st.session_state:
        st.session_state.estado_anterior = None
    if "respuesta" not in st.session_state:
        st.session_state.respuesta = None

    # Condiciones para cada estado de ánimo con botones
    if prediction[0][0] > 0.3 and st.session_state.estado_anterior != "feliz":
        st.header("Feliz")
        st.audio("1feliz.mp3", format="audio/mp3", start_time=0)
        client1.publish("misabela", "{'gesto': 'feliz'}", qos=0, retain=False)
        st.session_state.estado_anterior = "feliz"
        st.session_state.respuesta = None

    elif prediction[0][1] > 0.3 and st.session_state.estado_anterior != "triste":
        st.header("Triste")
        st.audio("1triste.mp3", format="audio/mp3", start_time=0)
        client1.publish("misabela", "{'gesto': 'triste'}", qos=0, retain=False)
        st.session_state.estado_anterior = "triste"
        st.session_state.respuesta = None

    elif prediction[0][2] > 0.3 and st.session_state.estado_anterior != "enojado":
        st.header("Enojado")
        st.audio("1enojada.mp3", format="audio/mp3", start_time=0)
        client1.publish("misabela", "{'gesto': 'enojado'}", qos=0, retain=False)
        st.session_state.estado_anterior = "enojado"
        st.session_state.respuesta = None

    # Mostrar botones de respuesta después de la emoción detectada
    if st.session_state.estado_anterior in ["feliz", "triste", "enojado"]:
        if st.session_state.respuesta is None:
            #st.write("¿Te gustaría escuchar otra canción relacionada?")
            if st.button("Sí"):
                st.session_state.respuesta = "si"
            elif st.button("No"):
                st.session_state.respuesta = "no"

        # Reproducir el audio según la respuesta
        if st.session_state.respuesta == "si":
            if st.session_state.estado_anterior == "feliz":
                st.audio("cancionfeliz.mp3", format="audio/mp3", start_time=0)
            elif st.session_state.estado_anterior == "triste":
                st.audio("canciontriste.mp3", format="audio/mp3", start_time=0)
            elif st.session_state.estado_anterior == "enojado":
                st.audio("cancionenojado.mp3", format="audio/mp3", start_time=0)
        elif st.session_state.respuesta == "no":
            st.audio("neutro.mp3", format="audio/mp3", start_time=0)

