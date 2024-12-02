import streamlit as st
import onnxruntime as rt
from extract_features import generar_datos 
import rembg
import numpy as np
from PIL import Image
import time

def main():
    margin = 255
    st.set_page_config(
        page_title="Detectar Papas Nativas",
        page_icon="🥔",
    )
    st.title("Papas app")
    st.write("¡Predice el tipo de papa entre 83 variedades!")
    uploaded_file = st.file_uploader("Sube una foto desde tu galería", type=['jpg', 'jpeg', 'png'])
    enable = st.checkbox("Activar cámara")
    file_camera = st.camera_input("Toma una foto", disabled= not enable)
    # if the app already has an image
    if file_camera or uploaded_file:
        input_array = np.array([])
        # select the one that is not null
        if file_camera:
            input_array = np.array(Image.open(file_camera))
        elif uploaded_file:
            input_array = np.array(Image.open(uploaded_file))
        datos = []
        with st.spinner("Quitando el fondo de la imagen..."):
            # remove the background of the image
            input_array = rembg.remove(input_array)
            # retrieve the image as an image and not as an array
            current_image = Image.fromarray(input_array)
            # set the size of the image
            width, height = current_image.size
            width_margin = width + 2 * margin
            height_margin = height + 2 * margin
            # get the new image
            final_image = Image.new("RGB", (width_margin, height_margin), (255,255,255))
            # put the element without the background into a white background
            final_image.paste(current_image, (255,255), current_image)
            # show the image
            st.image(final_image, caption="Imagen con el fondo removido")
            # turn the image into an array
            final_image_array = np.array(final_image)
            # generate the vector of characteristics
            datos = generar_datos(final_image_array)
            # map the forms to numerical data
            formas_dict = {"Alargado": 0, "Comprimido": 1, "Esf\u00e9rico": 2, "Irregular": 3, "Largo-Oblongo": 4, "Oblongo": 5, "Obovoide": 6, "Ovoide": 7, "Reniforme": 8}
            # get the vector of traits
            datos[0] = formas_dict[datos[0]]
            # turn it into a numpy array
            datos = np.array([datos], dtype=np.float32)
        # compute the prediction
        with st.spinner('Clasificando la papa'):
            session = rt.InferenceSession("random_forest_model.onnx")
            input_name = session.get_inputs()[0].name
            output_name = session.get_outputs()[0].name
            prediction = session.run([output_name], {input_name: datos})
            st.markdown("## Variedad nativa de papa detectada: " + str(prediction[0][0]))
    




if __name__ == "__main__":
    main()