import re
import streamlit as st
import pandas as pd
from pyairtable import Api # https://pyairtable.readthedocs.io/en/stable/getting-started.html
from datetime import datetime
import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
from rembg import remove
import onnxruntime
import time


st.set_page_config(
    page_title="Alex Silva - Portfolio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargamos fecha actual
today = datetime.today().strftime("%Y")

# Cargamos librerías de MaterializeCSS, Material Icons y Font Awesome


# https://materializecss.com/
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css">', unsafe_allow_html=True)
# https://materializecss.com/icons.html
st.markdown('<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">', unsafe_allow_html=True)
# https://fontawesome.com/start
st.markdown('<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css" rel="stylesheet">', unsafe_allow_html=True)

# Adicionamos estilos personalizados para mejorar el diseño
customStyle ="""
            <style type="text/css">
            /*Aumenta el tamaño de las cards*/
            .card.large{
                height:550px!important;
            }
            /*Aumenta el contenido disponible*/
            .card.large .card-content{
                max-height:fit-content!important;
            }
            /* Aumenta la fuente de los tabs de Streamlit*/
            button[data-baseweb="tab"] p{
                font-size:20px!important;
            }
            /* Remueve el espacio en el encabezado por defecto de las apps de Streamlit */
            div[data-testid="stAppViewBlockContainer"]{
                padding-top:0px;
            }
            /* Center text inside the contact input fields */
            div[data-testid="stTextInput"] input, 
            div[data-testid="stTextArea"] textarea {
                vertical-align: middle;
                height: 30px !important; /* Reduce height */
                padding: 5px !important; /* Adjust padding */
                font-size: 14px !important; /* Ensure text fits well */
            }
            </style>
            """
# Cargamos los estilos
st.html(customStyle)

# Cargamos la API Keu
AIRTABLE_API_KEY = st.secrets.AIRTABLE_API_KEY # Crea el token en este enlace https://airtable.com/create/tokens

# Seleccionamos el base id de Airtable
AIRTABLE_BASE_ID=st.secrets.AIRTABLE_BASE_ID #Copia la plantilla de este enlace https://airtable.com/appv1dCIP9oXJOXFE/shruOGxFeklRDFp0i/tblIBw5i2w5geQhQc/viwOxM9R5nUpGo3ZO?blocks=hide

# Creamos el objeto de Airtable
api = Api(AIRTABLE_API_KEY)
# Cargamos las tablas
tblprofile = api.table(AIRTABLE_BASE_ID, 'profile')
tblprojects = api.table(AIRTABLE_BASE_ID, 'projects')
tblskills = api.table(AIRTABLE_BASE_ID, 'skills')
tblContacts = api.table(AIRTABLE_BASE_ID, 'contacts')

# Cargamos los valores recuperados de las tablas

profile = tblprofile.all()[0]['fields']
name=profile['Name']
profileDescription=profile['Description']
profileTagline=profile['tagline']
linkedInLink=profile['linkedin']
# xLink=profile['x']
githubLink=profile['github']
picture=profile['picture'][0]['url']

def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email)

# def is_valid_phone(phone):
#     pattern = r"^\+?[1-9]\d{9,14}$"  # Supports international numbers
#     return re.match(pattern, phone)



# Creamos la plantilla de perfil con las clases CSS de MaterializeCSS 
# https://materializecss.com/
profileHTML=f"""
<div class="row">
<h1>{name} <span class="blue-text text-darken-3">Portfolio</span> </h1>
<h5>{profileTagline}</h5>
</div>
<div class="row">
    <div class="col s12 m12">
        <div class="card">
            <div class="card-content">
                <div class="row">                    
                    <div class="col s12 m2">
                        <img class="circle responsive-img" src="{picture}">
                    </div>
                        <div class="col s12 m10 ">
                            <span class="card-title">About me</span>
                            <p>{profileDescription}</p>
                            <div class="card-action">
                            <a href="{linkedInLink}" target="_blank" class="blue-text text-darken-3"><i class="fa-brands fa-linkedin fa-2xl"></i></i></a>
                            <a href="{githubLink}" target="_blank" class="blue-text text-darken-3"><i class="fa-brands fa-github fa-2xl"></i></a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
            """
# Mostramos el HTML generado
st.html(profileHTML)

# Creamos los tabs de Streamlit
tabSkils,tabPortfolio,tabContact =st.tabs(['My skills','My projects','Contact'])

def remove_background(image_url):
    try:
        # Download image from URL
        response = requests.get(image_url)
        response.raise_for_status()  # Ensure the request was successful

        # Convert image to numpy array
        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        
        # Decode image (force it to load as RGB)
        image = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED)

        # Ensure image has the correct number of channels (convert grayscale to RGB)
        if image is None:
            raise ValueError("Image could not be loaded.")

        if len(image.shape) == 2:  # Grayscale image
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:  # Convert from RGBA to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

        # Remove background
        image_no_bg = remove(image)

        return image_no_bg

    except Exception as e:
        print(f"Error processing image: {e}")
        return None
    
# Mostramos el tab de Skills
with tabSkils:
    skills=""
    # Hacemos el ciclo creando las plantillas de Skills
    for skill in tblskills.all(sort=['-Level']):
        # st.write(skill['fields'])
        skill=skill['fields']
        skillName = skill['Name']
        skillDescription = skill['Notes']    
        skillLevel = skill['Level']
        #skillImageList = skill.get('picture', [])
        #skillImage = skillImageList[0]['url'] if skillImageList else None
        #skillImage = skill['picture'][0]['url']
        # Add image if available
        # if skillImage:
        #     cleaned_img = remove_background(skillImage) # Clean background if needed
        #     #cleaned_img = skillImage
        #     skillImageHTML = f'<div style="text-align:center;"><img src="{cleaned_img}" width="80" height="80" style="border-radius:50%;"></div>'
        # else:
        #     skillImageHTML = ""
        skillStars=""
        # Creación de rating con estrellas
        for i in range(1,6):
            if i<=skillLevel:
                # Estrella completa
                skillStars=skillStars+'<i class="material-icons">star</i>'
            else:
                # Estrella vacía
                skillStars=skillStars+'<i class="material-icons">star_border</i>'
                
        skillYears = skill['startYear']   
        # Cálculo de años de experiencia
        skillExperience = int(today) -int(skillYears)
        # Plantilla del card de skill
        skillHTML = f"""                    
                <div class="col s12 m4">
                    <div class="card small">
                        <div class="card-content">
                            <span class="card-title">{skillName}</span>
                            <p>{skillDescription}</p>
                        </div>
                        <div class="card-action">
                            <div class="col s12 m6">
                                <p>Level:<br/> {skillStars}</p>
                            </div>
                            <div class="col s12 m6">
                                <p fon>Since:<br/> {skillYears} - More than {skillExperience} years</p>
                            </div>
                        </div>
                    </div>
                </div>
                    """
        skills=skills+skillHTML
    skillsHTML=f"""
            <div class="row">            
                {skills}       
            </div>       
        """     
    # Mostramos los skills
    st.html(skillsHTML) 
with tabPortfolio:       
    projects=""
    skillsHTML=""
    knowledgeHTML=""
    # Hacemos el ciclo creando las plantillas de proyectos
    for project in tblprojects.all():
        # st.write(skill['fields'])
        projectid= project['id']
        project=project["fields"]
        projectName = project['Name']        
        projectDescription = project['Description']    
        # Creamos la lista de Skills y Knowledge
        projectSkils = project['skills']
        skillsHTML=[f'<div class="chip green lighten-4">{p}</div>' for p in projectSkils]
        skillsHTML="".join(skillsHTML)
        projectKnowledge = project['Knowledge']        
        knowledgeHTML=[f'<div class="chip blue lighten-4">{p}</div>' for p in projectKnowledge]
        knowledgeHTML="".join(knowledgeHTML)
        
        projectLink = project['link'] 
        projectImageUrl = project['image'][0]['url']        
        # Plantilla de proyectos
        projectHTML = f"""                    
                <div class="col s12 m6">
                    <div class="card large">                    
                        <div class="card-image" style="height:200px">
                            <a href="{projectLink}"><img src="{projectImageUrl}"></a>
                        </div>                        
                        <div class="card-content">
                            <span class="card-title">{projectName}</span>                                                        
                            <p>{projectDescription}</p>
                            <div class="row hide-on-small-only">
                            <div class="col s12 m6">
                            <h6>Knowledge:</h6>
                            {knowledgeHTML}
                            </div>
                            <div class="col s12 m6">
                            <h6>Skills:</h6>
                            {skillsHTML}
                            </div>
                            </div>
                        </div>  
                        <div class="card-action right-align">
                        <a href="{projectLink}" target="_blank" class="waves-effect waves-light btn-large white-text blue darken-3"><i class="material-icons left">open_in_new</i>View</a>                        
                        </div>                                               
                    </div>
                </div>
                    """
        projects=projects+projectHTML
    projectsHTML=f"""
            <div class="row">            
                {projects}       
            </div>       
        """     
    # Mostramos los proyectos
    st.html(projectsHTML)        
with tabContact:
    st.info("If you think I can help you with some of your projects or entrepreneurships, send me a message I'll contact you as soon as I can. I'm always glad to help")
    with st.container(border=True):
        st.markdown("<h4 style='text-align: center;'>Contact Me</h4>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 3, 1])  # Centers the input fields

        with col2:
            parName = st.text_input("Your name", key="name", help="Enter your full name")
            parEmail = st.text_input("Your email", key="email", help="Enter a valid email")
            parPhoneNumber = st.text_input("WhatsApp phone number, with country code (optional)", key="phone")
            parNotes = st.text_area("What can I do for you", key="notes")

            # Validation
            email_valid = is_valid_email(parEmail)
            #phone_valid = is_valid_phone(parPhoneNumber)

            if parEmail and not email_valid:
                st.warning("⚠️ Please enter a valid email address (e.g., example@email.com).")

            # if parPhoneNumber and not phone_valid:
            #     st.warning("⚠️ Please enter a valid phone number (e.g., +1234567890).")

            #btnEnviar = st.button("Send", type="primary", disabled=not (email_valid and phone_valid))
            btnEnviar = st.button("Send", type="primary", disabled=not (email_valid ))
            
    # if btnEnviar:
    #     # Creamos el registro de contactos
    #     tblContacts.create({"Name":parName,"email":parEmail,"phoneNumber":parPhoneNumber,"Notes":parNotes})
    #     st.toast("Message sent")
    
    if btnEnviar:
        with st.spinner("Sending message..."):
            time.sleep(2)  # Simulating a delay for the message to be processed
            tblContacts.create({"Name": parName, "email": parEmail, "phoneNumber": parPhoneNumber, "Notes": parNotes})
        st.success("✅ Message sent successfully!")
        
st.markdown('<script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script>', unsafe_allow_html=True)