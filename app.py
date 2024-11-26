import streamlit as st
import onnxruntime as rt
from extract_features import generar_datos 
import rembg
import numpy as np
from PIL import Image


def main():
    margin = 255
    st.title("Papas app")
    st.write("¡Predice el tipo de papa entre 21 variedades!")
    enable = st.checkbox("Activar cámara")
    file_camera = st.camera_input("Toma una foto", disabled= not enable)
    if file_camera:
        input_array = np.array(Image.open(file_camera))
        input_array = rembg.remove(input_array)
        current_image = Image.fromarray(input_array)
        width, height = current_image.size
        width_margin = width + 2 * margin
        height_margin = height + 2 * margin
        final_image = Image.new("RGB", (width_margin, height_margin), (255,255,255))
        final_image.paste(current_image, (255,255), current_image)
        st.image(final_image)
        final_image_array = np.array(final_image)
        datos = generar_datos(final_image_array)
        formas_dict = {"Alargado": 0, "Comprimido": 1, "Esf\u00e9rico": 2, "Irregular": 3, "Largo-Oblongo": 4, "Oblongo": 5, "Obovoide": 6, "Ovoide": 7, "Reniforme": 8}
        datos[0] = formas_dict[datos[0]]
        datos = np.array([datos], dtype=np.float32)
        # st.write(datos)
        session = rt.InferenceSession("random_forest_model.onnx")
        input_name = session.get_inputs()[0].name
        output_name = session.get_outputs()[0].name
        prediction = session.run([output_name], {input_name: datos})
        st.write("Variedad detectada: ", prediction)





if __name__ == "__main__":
    main()