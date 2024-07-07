from flask import Flask, render_template, request, redirect, url_for, session,jsonify,Response,send_file
import io
from reportlab.pdfgen import canvas
import sqlite3
import pandas as pd
import cv2
import numpy as np
import mediapipe as mp
import time
import math
import datetime as dt
from flask_mail import Mail,Message
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

global username


mpMao = mp.solutions.hands #acede ao modulo sobre mãos presente na biblioteca do mediapipe
maos = mpMao.Hands(max_num_hands=1) #tudo o que é preciso para agora trabalharmos com mãos

mpDesenhar = mp.solutions.drawing_utils #esta é uma classe que ajuda a visualizar o resultado de uma tarefa do MediaPipe
video = cv2.VideoCapture(0) #captura o video da webcam embutida no pc. Para uma webcam externa, index=1 (talvez)


app = Flask(__name__) 
app.config['SERVER_NAME'] = '127.0.0.1:5000'  # Nome do servidor e porta
app.config['APPLICATION_ROOT'] = '/'          # Raiz da aplicação
app.config['PREFERRED_URL_SCHEME'] = 'http'    # Esquema de URL preferido


app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=587 
app.config['MAIL_USERNAME']='neurodrawpt@gmail.com'
app.config['MAIL_PASSWORD']='msfo nxfu ezgi rila'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail=Mail(app)

mpMao = mp.solutions.hands #acede ao modulo sobre mãos presente na biblioteca do mediapipe
maos = mpMao.Hands(max_num_hands=1) #tudo o que é preciso para agora trabalharmos com mãos

mpDesenhar = mp.solutions.drawing_utils #esta é uma classe que ajuda a visualizar o resultado de uma tarefa do MediaPipe
video = cv2.VideoCapture(0) #captura o video da webcam embutida no pc. Para uma webcam externa, index=1 (talvez)

app.secret_key = 'anivjvakev-3rgsgiud457-asmkoefsgj2546-gjerio'


app.config['erroQuadraticoMedioTotal'] = ''
app.config['PercentagemAcerto'] = ''
app.config['erroQuadraticoMedio'] = ''
app.config['ciclo'] = ''
app.config['Parar'] = ''
app.config['mascara3'] = ''
app.config['mascara6'] = ''
app.config['mascara5'] = ''
app.config['DATA'] = ''
app.config['segundos'] = ''



app.config['DATABASE'] = './database'
def get_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def gerarPDF():
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    dados=app.config.get('dados')
    print(dados)
    # Create a PDF document
    p.drawString(100, 750, "Relatório Médico")
 
    y = 700
    for linha in dados:
        p.drawString(100, y, f"Nome do Médico: {linha['NomeMedico']}")
        p.drawString(100, y - 20, f"Nome do Paciente: {linha['NomePaciente']}")
        #p.drawString(100, y - 40, f"Data: {linha['data']}")
        y -= 60
 
    p.showPage()
    p.save()
 
    buffer.seek(0)
    return buffer
 
db=get_db()
cursor=db.execute("update login set remember=0")
db.commit()

def gen_frames():

    
    Dificuldade=app.config.get('Dificuldade')
    
    if Dificuldade=="Facil":
        pontosX =  np.arange(0,440)
        pontosY =  100*np.sin(pontosX/28)+240
        pontosY = pontosY.astype(int)
        pontosX = pontosX + 100
        
    elif Dificuldade=="Medio":
        pontosX =  np.arange(0,440)
        pontosY =  100*np.sin(1.4*pontosX/28)+240
        pontosY = pontosY.astype(int)
        pontosX = pontosX + 100
    
    else:
        pontosX =  np.arange(0,440)
        pontosY =  100*np.sin(2*pontosX/28)+240
        pontosY = pontosY.astype(int)
        pontosX = pontosX + 100
    
    DATA = dt.datetime.today().strftime("%d/%m/%Y")
    app.config['DATA']=DATA
    #Para calcular os FPS da camara:
    TempoInicial = 0

    #Temos de saber a primeira vez que o programa é corrido:
    
    k=0
    CapturaVideo1=0
    CoordenadasDedoInicial=[0,0]
    mascara1 = 0
    mascara3 = 0
    mascara5 = 0
    mascara6 = 0
    desenhar = 0
    b=0
    a=0
    erroQuadraticoMedio = 0. #vai ser um float
    ciclo = 0
    erroQuadraticoMedioTotal = 0.
    Comeca_contar=0
    PercentagemAcerto=0
    segundos=0
    Parar = 0
    video = cv2.VideoCapture(0) #captura o video da webcam embutida no pc. Para uma webcam externa, index=1 (talvez)

    
    while True:

        abre,CapturaVideo=video.read()
        CapturaVideo = cv2.flip(CapturaVideo, 1) #faz o espelho do video
        videoLargura = video.get(cv2.CAP_PROP_FRAME_WIDTH) #qual a largura do frame da camara
        videoAltura = video.get(cv2.CAP_PROP_FRAME_HEIGHT) #qual a altura do frame da camara

        mascara = np.zeros_like(CapturaVideo) #a cada ciclo as mascaras serão uma imagem com tudo a zeros com as dimensões 640x480
        mascara2 = np.zeros_like(CapturaVideo)
        mascara4 = np.zeros_like(CapturaVideo)
        
        if not abre:
            break

        TempoAgora=time.time() #vai buscar o tempo neste preciso instante, literalmente
        FPS = int(1/(TempoAgora-TempoInicial)) #a conversão para int deve-se a querermos numeros inteiros, senão teriamos numeros decimais
        TempoInicial = TempoAgora #é preciso atualizar a váriavel TempoInicial porque não pode ser sempre zero
            
        resultado = maos.process(cv2.cvtColor(CapturaVideo, cv2.COLOR_BGR2RGB)) #A ordem das cores do OpenCV é BGR, então para processar as imagens temos de converter para RGB para ter significado no futuro

        CoordenadasBotaoIniciar = [70,220] #Coordenadas de todos os botões presentes na imagem
        CoordenadasBotaoParar = [580,220]

        CapturaVideo1 = CapturaVideo #A captura de video vai agora chamar-se CapturaVideo1 para podermos trabalhar sobre a imagem recebida e aplicar mascaras
        

        if resultado.multi_hand_landmarks: #se conseguimos detetar uma mão

            DedoIndicador = resultado.multi_hand_landmarks[0].landmark[mpMao.HandLandmark.INDEX_FINGER_TIP]  #vai focar no dedo indicador em vez de ser na mão toda
            CoordenadasDedoFinal = mpDesenhar._normalized_to_pixel_coordinates(DedoIndicador.x, DedoIndicador.y, videoLargura, videoAltura) #vai calcular as coordenadas do dedo 
                
            if (CoordenadasDedoFinal!=None):
            
                cv2.circle(CapturaVideo1,CoordenadasBotaoIniciar,30,(0,255,0),-1)#parâmetros de entrada: (image, center_coordinates, radius, color em BGR, thickness) ->  https://www.geeksforgeeks.org/python-opencv-cv2-circle-method/
                cv2.putText(CapturaVideo1, "Iniciar",[CoordenadasBotaoIniciar[0]-22,CoordenadasBotaoIniciar[1]+2], cv2.FONT_HERSHEY_TRIPLEX, 0.4, (0,0,0), 1)
                cv2.circle(CapturaVideo1,CoordenadasBotaoParar,30,(0,0,255),-1)#parâmetros de entrada: (image, center_coordinates, radius, color em BGR, thickness) ->  https://www.geeksforgeeks.org/python-opencv-cv2-circle-method/
                cv2.putText(CapturaVideo1, "Parar",[CoordenadasBotaoParar[0]-20,CoordenadasBotaoParar[1]+5], cv2.FONT_HERSHEY_TRIPLEX, 0.4, (0,0,0), 1)
                cv2.putText(CapturaVideo1, f"Dificuldade: {Dificuldade}",[10,15], cv2.FONT_HERSHEY_TRIPLEX, 0.4, (0,0,0), 1)
                cv2.circle(CapturaVideo1, CoordenadasDedoFinal, 2, (76,171,206), 3) #parâmetros de entrada: (image, center_coordinates, radius, color em BGR, thickness) ->  https://www.geeksforgeeks.org/python-opencv-cv2-circle-method/

                    #equação do Modulo da distancia entre 2 pontos:
                equacaoIniciar = (CoordenadasBotaoIniciar[0]-CoordenadasDedoFinal[0])**2+(CoordenadasBotaoIniciar[1]-CoordenadasDedoFinal[1])**2
                if (equacaoIniciar)<800:
                    desenhar = 1
                    tempo_inicio = time.time()
                    Comeca_contar = 1
                    

                equacaoParar = (CoordenadasBotaoParar[0]-CoordenadasDedoFinal[0])**2+(CoordenadasBotaoParar[1]-CoordenadasDedoFinal[1])**2
                if (equacaoParar)<800:
                    desenhar = 0
                    k = 0
                    Parar = 1
                    app.config['Parar'] = Parar
                    if Comeca_contar == 1:
                        Comeca_contar = 0
                        tempo_final = time.time()
                        segundos = tempo_final - tempo_inicio
                        segundos = round(segundos,2)
                        app.config['segundos']=segundos
                    break

                if desenhar == 1:  
                    if k<1:
                        CoordenadasDedoInicial = CoordenadasDedoFinal

                        while a<439:  
                            CoordenadasPontos = [pontosX[a],pontosY[a]]
                            mascara2 = cv2.line(mascara2,CoordenadasPontos,[pontosX[a+1],pontosY[a+1]],(255,255,255),1)
                            mascara3 = mascara3 + mascara2
                            a=a+1

                        k+=1
                        
                    elif k==1:
                        i=0
                        erroQuadraticoMedio=0
                        pontos =  np.arange(40,610)
                        if CoordenadasDedoFinal[0] in pontos:
                            mascara = cv2.line(mascara, CoordenadasDedoFinal, CoordenadasDedoInicial, (255,255,255), 5)  #para desenhar naquele ponto // parametros entrada: cv2.line(image, start_point, end_point, color, thickness)   -> https://www.geeksforgeeks.org/python-opencv-cv2-line-method/  
                            
                            if CoordenadasDedoFinal[0] in pontosX:

                                i = list(pontosX).index(CoordenadasDedoFinal[0])
                                erroQuadraticoMedio = math.fabs(CoordenadasDedoFinal[1]-pontosY[i])
                                erroQuadraticoMedio = float(erroQuadraticoMedio**2)

                                if erroQuadraticoMedio <50:
                                    mascara4 = cv2.line(mascara4, CoordenadasDedoFinal, CoordenadasDedoInicial, (0,255,0), 3)  #para desenhar naquele ponto // parametros entrada: cv2.line(image, start_point, end_point, color, thickness)   -> https://www.geeksforgeeks.org/python-opencv-cv2-line-method/  
                                elif (erroQuadraticoMedio >=50 and erroQuadraticoMedio <70):
                                    mascara4 = cv2.line(mascara4, CoordenadasDedoFinal, CoordenadasDedoInicial, (0,255,255), 3)  #para desenhar naquele ponto // parametros entrada: cv2.line(image, start_point, end_point, color, thickness)   -> https://www.geeksforgeeks.org/python-opencv-cv2-line-method/  
                                else:
                                    mascara4 = cv2.line(mascara4, CoordenadasDedoFinal, CoordenadasDedoInicial, (0,0,255), 3)  #para desenhar naquele ponto // parametros entrada: cv2.line(image, start_point, end_point, color, thickness)   -> https://www.geeksforgeeks.org/python-opencv-cv2-line-method/  

                                mascara6 = mascara6 + mascara
                                mascara5 = mascara5 + mascara4 + mascara3

                            mascara1 = mascara1 + mascara + mascara3
                            CapturaVideo1 = cv2.add(CapturaVideo1,mascara1)
                            CoordenadasDedoInicial = CoordenadasDedoFinal

                        ciclo += 1
                        app.config['ciclo']=ciclo
                        erroQuadraticoMedioTotal = float(erroQuadraticoMedioTotal + erroQuadraticoMedio)
                        app.config['erroQuadraticoMedioTotal']=erroQuadraticoMedioTotal
                        app.config['mascara3'] = mascara3
                        app.config['mascara6'] = mascara6
                        app.config['mascara5'] = mascara5
                        
            else:
                print("O dedo não se encontra visível!")

        else:
            cv2.putText(CapturaVideo1, "Nao consigo detetar a tua mao", (100,50), cv2.FONT_HERSHEY_TRIPLEX, 0.8, (0,0,0), 1)  #vai escrever  o numero de FPS no video // Sintaxe: cv2.putText(image, text, org, font, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]]) -> https://www.geeksforgeeks.org/python-opencv-cv2-puttext-method/ 


        cv2.putText(CapturaVideo1, f"FPS: {str(FPS)}", (10,475), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (76,171,206), 1)  #vai escrever  o numero de FPS no video // Sintaxe: cv2.putText(image, text, org, font, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]]) -> https://www.geeksforgeeks.org/python-opencv-cv2-puttext-method/ 
    
        
        ret,buffer=cv2.imencode('.jpg',CapturaVideo1)
        CapturaVideo=buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + CapturaVideo + b'\r\n')
        


        
#INICIO DA APLICAÇÃO 
@app.route("/",methods=["GET","POST"])
def MenuInicial():
    return render_template("paginainicial.html")

@app.route("/contactar",methods=['GET','POST'])
def contactar():
    if request.method == 'POST':
        db=get_db()
        DPrimeiroNome = request.form['PrimeiroNome']
        DUltimoNome = request.form['UltimoNome']
        DEmail = request.form['Email']
        DDescricao = request.form['Mensagem']

        _,sufixo=DEmail.split('@')
        sufixos_populares = {"isep.ipp.pt","hotmail.com", "gmail.com", "yahoo.com", "outlook.com", "aol.com", "icloud.com", "mail.com", "protonmail.com", "zoho.com", "yandex.com", "gmx.com", "inbox.com", "live.com"}        
        if sufixo in sufixos_populares:    
            cursor = db.execute("INSERT INTO contacto(PrimeiroNomeContacto,UltimoNomeContacto,EmailContacto,DescricaoContacto,estado)VALUES(?,?,?,?,'0')",(DPrimeiroNome,DUltimoNome,DEmail,DDescricao))
            db.commit() 
            return redirect(url_for('MenuInicial'))
        else:
            return render_template("contactar.html", erro="Insira um sufixo de e-mail válido, por favor.")
        
    return render_template("contactar.html")


@app.route("/login", methods=['GET','POST']) 
def login(): 
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        remember_me = request.form.get('remember_me')
        db=get_db()
        cursor=db.execute("SELECT * FROM login WHERE login = ? AND password = ?", (username, password))
        user=cursor.fetchone()
        
        if user:
            session['username'] =username
            sql="select ID from login where login="+str(username)
            df=pd.read_sql(sql,db)
            Funcao=int(df['ID'].iloc[0])
            db.close()
            session['Funcao']=Funcao
            if remember_me:
                db=get_db()
                cursor=db.execute("update login set remember=1 where login=?",((username),))
                db.commit()

            return redirect(url_for('Portal'))
        else:
            return render_template('login.html', erro = 'Credenciais Inválidas: Impossível aceder ao sistema.')
    
    db=get_db()
    cursor=db.execute("select login from login where remember<>0")
    user=cursor.fetchone()
    

    if user:
        user=user[0]
        session['username'] =user
        sql="select ID from login where login="+str(user)
        df=pd.read_sql(sql,db)
        Funcao=int(df['ID'].iloc[0])
        db.close()
        session['Funcao']=Funcao
        return redirect('Portal')
    else:
        return render_template('login.html')

@app.route("/register",methods=['GET','POST'])
def register():
    if request.method =='POST':
        username=request.form['Dusername']
        password=request.form['Dpassword']
        ID=request.form['ID_funcao']
        db=get_db()
        
        #try:
        if len(username)==9 and username.isdigit():
            if ID=='2':
                try:
                    cursor=db.execute("insert into login(login,password,ID) values(?,?,?)",(int(username),password,int(ID)))
                    db.commit()
                    cursor=db.execute("insert into Medicos(NIF_Login,Info) values(?,0)",(int(username),))
                    db.commit()
                except:
                    db.close()
                    app.config["erroRegisto"]=1
                    return redirect(url_for('register'))
            elif ID=='3':
                try:
                    cursor=db.execute("insert into login(login,password,ID) values(?,?,?)",(int(username),password,int(ID)))
                    db.commit()
                    cursor=db.execute("insert into Pacientes(NIF,Info) values(?,0)",(int(username),))
                    db.commit()
                except:
                    db.close()
                    app.config["erroRegisto"]=1
                    return redirect(url_for('register'))
            else:
                return render_template('register.html',mensagemID='Por favor escolha uma função!')
        else:
            return render_template('register.html',mensagemUser='Por favor introduza um NIF válido. Apenas são aceites 9 dígitos')
        
        db.close()
        app.config["usernameRegisto"]=username
        return redirect(url_for('get_coordinates'))
        #except:
            #return render_template('register.html',erro="Credenciais inválidas. Reveja o seu NIF e tente novamente.")

    if app.config.get("erroRegisto")==1: 
        app.config["erroRegisto"]=0
        return render_template('register.html',erro=1)
    else:
        return render_template('register.html')

@app.route("/get_coordinates",methods=["GET","POST"])
def get_coordinates():
    if request.method == 'POST':
        lat = request.form.get('lat')
        lon = request.form.get('lon')
        username = app.config.get("usernameRegisto")
        db=get_db()
        cursor=db.execute("UPDATE login SET latitude=?,longitude=?,remember=0 where login=?",(lat,lon,username))
        db.commit()
        return redirect(url_for('login'))
    
    return render_template("get_coordinates.html")



@app.route("/SaberMais",methods=["GET","POST"])
def MenuSaberMais():
    markers=''
    id = 1
    db=get_db()
    df=pd.read_sql("select latitude,longitude from login",db)
    db.close()
    for i in range(len(df)):
        idd = 'Marcador'+str(id)
        id +=1
        lat=float(df['latitude'][i])
        lon=float(df['longitude'][i])
        markers += "var {idd} = L.marker([{latitude}, {longitude}]);\
                    {idd}.addTo(map);".format(idd=idd,latitude=lat,longitude=lon)
        
    return render_template("sabermais.html",markers=markers)



#APÓS LOGIN
@app.route("/Portal",methods=["GET","POST"])
def Portal():

    db=get_db()
    username=session['username']
    sql="select ID from login where login="+str(username)
    df=pd.read_sql(sql,db)
    Funcao=int(df['ID'].iloc[0])
    if Funcao==1:
        sql="select Nome,Apelido from Admins where NIF="+str(username)
        varAuxiliar = 'Eng.'
    elif Funcao==2:
        sql="select Nome,Apelido from Medicos where NIF_Login="+str(username)
        varAuxiliar = 'Dr.'
    else:
        sql="select Nome,Apelido from Pacientes where NIF="+str(username)
        varAuxiliar = ''


    cursor = db.execute("select Descricao from Evento")
    ListaEventos=cursor.fetchall()
    df=pd.read_sql(sql,db)
    cursor=db.execute("select * from Presenca")
    presencas = cursor.fetchall()
    ListaPresenca=[]
    for linha in presencas:
        dados = {
            "ID":linha[0],
            "Descricao":linha[1]
        }
        ListaPresenca.append(dados)

    db=get_db()
    cursor=db.execute("SELECT COUNT(*) AS NUMERO FROM Mensagens WHERE NIF_Destinatario = ? AND Estado = 'Não Lida'",(session['username'],))
    nrMensagens=cursor.fetchone()
    nrMensagens=nrMensagens[0]


    try:
        Nome = df['Nome'].iloc[0]
        Apelido = df['Apelido'].iloc[0]
        var = 1
        
        if Funcao==2: #se são médicos
            data = dt.datetime.today().strftime("%d/%m/%Y")
            db=get_db()
            cursor=db.execute("select ID,Info from Medicos where NIF_Login=?",(str(username),))
            result = cursor.fetchone()
            IDMedico = str(result[0])
            Info=str(result[1])
            cursor=db.execute("select ID,Nome,Apelido,Idade,ID_Sexo,Email from Pacientes where ID_Medico=?",(IDMedico,))
            ListaPacientes = cursor.fetchall()
            if Info=='1':
                #PARA Marcacoes ANTERIORES
                cursor=db.execute("select ID,ID_Paciente,ID_Evento,Dte,ID_Presenca from Marcacao where ID_Medico=? AND DATETIME(Dte) < DATETIME('now') order by Dte desc",(IDMedico,))
                ListaMarcacoesPassadas = cursor.fetchall()
                ListaMarcacoes_passadas=[]

                for linha in ListaMarcacoesPassadas:
                    Data,Hora = linha[3].split(" ")
                    ano,mes,dia = Data.split("-")
                    Data = dia+"/"+mes+"/"+ano
                    hour,mins,sec = Hora.split(":")
                    Hora=hour+":"+mins
                    dados_do_exame = {
                        "ID":linha[0],
                        "ID_Paciente": linha[1],
                        "ID_Evento":linha[2],
                        "Dia": Data,
                        "Hora": Hora,
                        "ID_Presenca":linha[4]
                    }
                    ListaMarcacoes_passadas.append(dados_do_exame)


                #PARA Marcacoes FUTUROS
                cursor=db.execute("select ID,ID_Paciente,ID_Evento,Dte from Marcacao where ID_Medico=? AND DATETIME(Dte) >= DATETIME('now') order by Dte",(IDMedico,))
                ListaMarcacoesFuturas = cursor.fetchall()
                ListaMarcacoes_futuras=[]

                for linha in ListaMarcacoesFuturas:
                    Data,Hora = linha[3].split(" ")
                    ano,mes,dia = Data.split("-")
                    Data = dia+"/"+mes+"/"+ano
                    hour,mins,sec = Hora.split(":")
                    Hora=hour+":"+mins
                    dados_do_exame = {
                        "ID":linha[0],
                        "ID_Paciente": linha[1],
                        "ID_Evento":linha[2],
                        "Dia": Data,
                        "Hora": Hora,
                    }
                    ListaMarcacoes_futuras.append(dados_do_exame)
                db.close()
                app.config["ListaMarcacoesPassadas"]=ListaMarcacoes_passadas

                db=get_db()
                cursor=db.execute("select Nome,Apelido from Pacientes P join Exames E where P.ID=E.ID_Paciente and E.ID_Medico=? order by E.ID desc",(IDMedico,))
                lista=cursor.fetchall()
                ListaNotifics = []
                for item in lista:
                    dados={
                        "Nome":item[0],
                        "Apelido":item[1],
                        "tema":"exames"
                    }
                    ListaNotifics.append(dados)

                app.config["Notificações"] = ListaNotifics

                return render_template("InicioPortal.html",ListaNotifics=ListaNotifics,data=data,ListaPresenca=ListaPresenca,nrMensagens=nrMensagens,ListaEventos=ListaEventos,Nome=Nome,Apelido=Apelido,abreviatura=varAuxiliar,Funcao=Funcao,var=var,ListaPacientes=ListaPacientes,ListaMarcacoesFuturas=ListaMarcacoes_futuras,ListaMarcacoesPassadas=ListaMarcacoes_passadas)
            else:
                mensagem="Por favor, aceda à secção 'Gerir Conta' para atualizar os seus dados."
                return render_template("InicioPortal.html",data=data,ListaPresenca=ListaPresenca,nrMensagens=nrMensagens,ListaEventos=ListaEventos,Nome=Nome,Apelido=Apelido,abreviatura=varAuxiliar,Funcao=Funcao,var=var,ListaPacientes=ListaPacientes,mensagem2=mensagem,mensagem=mensagem)

            
        elif Funcao==3: #se são pacientes
            data = dt.datetime.today().strftime("%d/%m/%Y")

            db=get_db()
            cursor=db.execute("select ID,ID_Medico,Info from Pacientes where NIF=?",(str(username),))
            result = cursor.fetchone()
            IDPaciente = str(result[0])
            IDMedico=str(result[1])
            Info=str(result[2])
        
            if Info == '1':
                cursor=db.execute("select count(ID) from Exames where ID_Paciente=?",(IDPaciente))
                result = cursor.fetchone()
                if result:
                    varAux = int(result[0])
                else:
                    varAux=0

                db=get_db()
                cursor=db.execute("select Nome,Apelido,ID_Especialidade,ID_Sexo from Medicos where ID=?",str(IDMedico))
                Medico = cursor.fetchone()

                InfoMedico = {
                    "Nome": Medico[0],
                    "Apelido": Medico[1],
                    "ID_Especialidade": Medico[2],
                    "ID_Sexo": Medico[3]
                }

                

                #PARA EXAMES ANTERIORES
                cursor=db.execute("select ID_Medico,Dte from Marcacao where ID_Paciente=? AND ID_Evento='1' AND DATETIME(Dte) < DATETIME('now') order by Dte",(IDPaciente))
                exames = cursor.fetchall()

                if exames:
                    lista_de_examesPassados=[]

                    for linha in exames:
                        Data,Hora = linha[1].split(" ")
                        ano,mes,dia = Data.split("-")
                        Data = dia+"/"+mes+"/"+ano
                        hour,mins,sec = Hora.split(":")
                        Hora=hour+":"+mins
                        dados_do_exame = {
                            "ID_Medico": linha[0],
                            "Dia": Data,
                            "Hora": Hora
                        }
                        lista_de_examesPassados.append(dados_do_exame)
                else:
                    lista_de_examesPassados=0

                

                #PARA EXAMES FUTUROS
                cursor=db.execute("select ID_Medico,Dte from Marcacao where ID_Paciente=? AND ID_Evento='1' AND DATETIME(Dte) >= DATETIME('now') order by Dte",(IDPaciente))
                exames = cursor.fetchall()
                
                if exames:
                    lista_de_examesFuturos=[]

                    for linha in exames:
                        Data,Hora = linha[1].split(" ")
                        ano,mes,dia = Data.split("-")
                        Data = dia+"/"+mes+"/"+ano
                        hour,mins,sec = Hora.split(":")
                        Hora=hour+":"+mins
                        dados_do_exame = {
                            "ID_Medico": linha[0],
                            "Dia": Data,
                            "Hora": Hora
                        }
                        lista_de_examesFuturos.append(dados_do_exame)
                else:
                    lista_de_examesFuturos=0

                #PARA CONSULTAS ANTERIORES
                cursor=db.execute("select ID_Medico,Dte from Marcacao where ID_Paciente=? AND ID_Evento='2' AND DATETIME(Dte) < DATETIME('now') order by Dte",(IDPaciente))
                Consultas = cursor.fetchall()
                
                if Consultas:
                    lista_de_consultasPassadas=[]

                    for linha in Consultas:
                        Data,Hora = linha[1].split(" ")
                        ano,mes,dia = Data.split("-")
                        Data = dia+"/"+mes+"/"+ano
                        hour,mins,sec = Hora.split(":")
                        Hora=hour+":"+mins
                        dados_do_exame = {
                            "ID_Medico": linha[0],
                            "Dia": Data,
                            "Hora": Hora
                        }
                        lista_de_consultasPassadas.append(dados_do_exame)
                else:
                    lista_de_consultasPassadas=0


                #PARA CONSULTAS FUTUROS
                cursor=db.execute("select ID_Medico,Dte from Marcacao where ID_Paciente=? AND ID_Evento='2' AND DATETIME(Dte) >= DATETIME('now') order by Dte",(IDPaciente))
                Consultas = cursor.fetchall()
                
                if Consultas:
                    lista_de_consultasFuturas=[]

                    for linha in Consultas:
                        Data,Hora = linha[1].split(" ")
                        ano,mes,dia = Data.split("-")
                        Data = dia+"/"+mes+"/"+ano
                        hour,mins,sec = Hora.split(":")
                        Hora=hour+":"+mins
                        dados_do_exame = {
                            "ID_Medico": linha[0],
                            "Dia": Data,
                            "Hora": Hora
                        }
                        lista_de_consultasFuturas.append(dados_do_exame)
                else:
                    lista_de_consultasFuturas=0


                cursor=db.execute("select ID_Evento,Dte from Marcacao where ID_Paciente=? and ID_Evento=1 order by Dte desc",(IDPaciente))
                lista=cursor.fetchall()
                ListaNotifics = []
                for item in lista:
                    dados={
                        "ID_Evento":item[0],
                        "data":item[1],
                        "tema":"exames"
                    }
                    ListaNotifics.append(dados)


                cursor=db.execute("select ID_Evento,Dte from Marcacao where ID_Paciente=? and ID_Evento=2 order by Dte desc",(IDPaciente))
                lista=cursor.fetchall()
                for item in lista:
                    dados={
                        "ID_Evento":item[0],
                        "data":item[1],
                        "tema":"consulta"
                    }
                    ListaNotifics.append(dados)

                app.config["Notificações"] = ListaNotifics

                print(ListaNotifics)

                return render_template("InicioPortal.html",varAux=varAux,ListaNotifics=ListaNotifics,nrMensagens=nrMensagens,ListaEventos=ListaEventos,Nome=Nome,Apelido=Apelido,abreviatura=varAuxiliar,Funcao=Funcao,var=1,ListaExamesFuturos=lista_de_examesFuturos,ListaConsultasPassadas=lista_de_consultasPassadas,ListaConsultasFuturas=lista_de_consultasFuturas,ListaExamesPassados=lista_de_examesPassados,Medico=InfoMedico,DataAtual=data)
            else:
                return render_template("InicioPortal.html",varAux=varAux,nrMensagens=nrMensagens,ListaEventos=ListaEventos,Nome=Nome,Apelido=Apelido,abreviatura=varAuxiliar,Funcao=Funcao,var=0,mensagem="Por favor, atualize os seus dados na secção 'Gerir Conta'.")


        else: #se são administradores
            db=get_db()
            #marcações futuras
            cursor=db.execute("select * from Marcacao where DATETIME(Dte) >= DATETIME('now') order by Dte")
            listaConsultasFuturas = cursor.fetchall()
            lista_de_consultasFuturas=[]

            for linha in listaConsultasFuturas:
                Data,Hora = linha[4].split(" ")
                ano,mes,dia = Data.split("-")
                Data = dia+"/"+mes+"/"+ano
                hour,mins,sec = Hora.split(":")
                Hora=hour+":"+mins
                cursor=db.execute("select Nome,Apelido from Medicos where ID=?",linha[1])
                Nomes=cursor.fetchone()
                NomeMedico=Nomes[0]+' '+Nomes[1]
                cursor=db.execute("select Nome,Apelido from Pacientes where ID=?",linha[2])
                Nomes=cursor.fetchone()
                NomePaciente=Nomes[0]+' '+Nomes[1]
                dados_do_exame = {
                    "ID":linha[0],
                    "NomeMedico": NomeMedico,
                    "NomePaciente":NomePaciente,
                    "ID_Evento":linha[3],
                    "Dia": Data,
                    "Hora": Hora
                }
                lista_de_consultasFuturas.append(dados_do_exame)
            
            #marcações passadas
            cursor=db.execute("select * from Marcacao where DATETIME(Dte) < DATETIME('now') order by Dte")
            listaConsultasPassadas = cursor.fetchall()
            lista_de_consultasPassadas=[]

            for linha in listaConsultasPassadas:
                Data,Hora = linha[4].split(" ")
                ano,mes,dia = Data.split("-")
                Data = dia+"/"+mes+"/"+ano
                hour,mins,sec = Hora.split(":")
                Hora=hour+":"+mins
                cursor=db.execute("select Nome,Apelido from Medicos where ID=?",linha[1])
                Nomes=cursor.fetchone()
                NomeMedico=Nomes[0]+' '+Nomes[1]
                cursor=db.execute("select Nome,Apelido from Pacientes where ID=?",linha[2])
                Nomes=cursor.fetchone()
                NomePaciente=Nomes[0]+' '+Nomes[1]
                dados_do_exame = {
                    "ID":linha[0],
                    "NomeMedico": NomeMedico,
                    "NomePaciente":NomePaciente,
                    "ID_Evento":linha[3],
                    "Dia": Data,
                    "Hora": Hora
                }
                lista_de_consultasPassadas.append(dados_do_exame)

            cursor=db.execute("SELECT ID,Nome,Apelido,Idade,NrCC,Email,ID_Sexo,'Paciente' AS Tipo FROM Pacientes where ID_Atividade=1 UNION SELECT ID,Nome,Apelido,Idade,NrCC,Mail,ID_Sexo,'Médico' AS Tipo FROM Medicos where ID_Atividade=1")
            listaUtilizadores = cursor.fetchall()

            listaUsers = []
            for linha in listaUtilizadores:
                dados={
                    "ID":linha[0],
                    "Nome":linha[1],
                    "Apelido":linha[2],
                    "Idade":linha[3],
                    "NrCC":linha[4],
                    "Email":linha[5],
                    "ID_Sexo":linha[6],
                    "Tipo":linha[7]
                }
                listaUsers.append(dados)

            cursor=db.execute("select * from contacto")
            lista=cursor.fetchall()
            FormsdeContacto=[]
            for item in lista:
                dados={
                    "ID":item[0],
                    "Nome":item[1],
                    "Apelido":item[2],
                    "Email":item[3],
                    "Descricao":item[4],
                    "Estado":item[5]
                }
                FormsdeContacto.append(dados)

            cursor=db.execute("select PrimeiroNomeContacto,UltimoNomeContacto from contacto order by ID desc")
            lista=cursor.fetchall()
            ListaNotifics = []
            for item in lista:
                dados={
                    "Nome":item[0],
                    "Apelido":item[1],
                    "tema":"formularioContacto"
                }
                ListaNotifics.append(dados)

            cursor=db.execute("select Nome,Apelido from Medicos where Nome not null order by ID desc")
            lista=cursor.fetchall()
            for item in lista:
                dados={
                    "Nome":item[0],
                    "Apelido":item[1],
                    "tema":"medicos"
                }
                ListaNotifics.append(dados)


            cursor=db.execute("select Nome,Apelido from Pacientes where Nome not null order by ID desc")
            lista=cursor.fetchall()
            for item in lista:
                dados={
                    "Nome":item[0],
                    "Apelido":item[1],
                    "tema":"pacientes"
                }
                ListaNotifics.append(dados)

            cursor=db.execute("select Nome,Apelido from Pacientes P join Exames E where P.ID=E.ID_Paciente order by E.ID desc")
            lista=cursor.fetchall()
            for item in lista:
                dados={
                    "Nome":item[0],
                    "Apelido":item[1],
                    "tema":"exames"
                }
                ListaNotifics.append(dados)

            app.config["Notificações"] = ListaNotifics

            return render_template("InicioPortal.html",ListaNotifics=ListaNotifics,ContactForms=FormsdeContacto,nrMensagens=nrMensagens,ListaUtilizadores=listaUsers,listaConsultasPassadas=lista_de_consultasPassadas,listaConsultasFuturas=lista_de_consultasFuturas,ListaEventos=ListaEventos,Nome=Nome,Apelido=Apelido,abreviatura=varAuxiliar,Funcao=Funcao,var=var)
    except:
        var = 0
        return render_template("InicioPortal.html",nrMensagens=nrMensagens,Funcao=Funcao,var=var,erro="Ainda não preencheu os seus dados. Vá a 'Gerir Conta' e preencha-os, por favor.")

@app.route("/forms",methods=["GET","POST"])
def forms():
    if request.method=="POST":
        id=app.config.get('ID_forms')
        db=get_db()
        cursor=db.execute("select EmailContacto from contacto where id=?",id)
        recipient=cursor.fetchone()
        recipient=recipient[0]
        if session['username'] == '252418018':
            x=("Rafael do NeuroDraw",'neurodrawpt@gmail.com')
        elif session['username'] == '238101002':
            x=("Maria do NeuroDraw",'neurodrawpt@gmail.com')
        else:
            x=("Mónica do NeuroDraw",'neurodrawpt@gmail.com')

        message = Message(
            subject='Agradecemos por nos contactar',
            recipients=[recipient],
            sender=x
        )
        texto=request.form["fname"]
        message.html=texto+'<br><p>Com os melhores cumprimentos,</p><p><em>A Equipa do <b>NeuroDraw</b></p></em>'
        mail.send(message)
        cursor=db.execute("update contacto set estado='1',resposta=? where id=?",(texto,id))
        db.commit()
        db.close()
        return redirect(url_for('Portal'))
    else:
        id=request.args.get('id')
        app.config["ID_forms"]=id
        db=get_db()
        cursor=db.execute("select * from contacto where id=?",id)
        lista=cursor.fetchone()
    
        FormsdeContacto={
            "Nome":lista[1],
            "Apelido":lista[2],
            "Email":lista[3],
            "Descricao":lista[4],
            "Estado":lista[5]
        }

        return render_template("ResponderForms.html",FormsdeContacto=FormsdeContacto)
        




@app.route("/GerirConta",methods=["GET","POST"])
def GerirConta():
    if request.method=='POST':
        db=get_db()
        Nome = request.form['PrimeiroNome']
        Apelido = request.form['UltimoNome']
        Sexo = int(request.form['Sexo'])
        Idade = int(request.form['Idade'])
        Email = request.form['Email']
        Telemovel = int(request.form['Telemovel'])
        NrCC = int(request.form['NrCC'])

        if session['Funcao']==2:
            Especialidade = int(request.form['Especialidade'])

            cursor = db.execute("select ID from Medicos where Mail=? and NIF_Login<>?",(Email,session['username']))
            var1=cursor.fetchone()
            cursor = db.execute("select ID from Medicos where Telemovel=? and NIF_Login<>?",(Telemovel,session['username']))
            var2=cursor.fetchone()
            cursor = db.execute("select ID from Medicos where NrCC=? and NIF_Login<>?",(NrCC,session['username']))
            var3=cursor.fetchone()
            cursor = db.execute("select ID from Pacientes where Email=?",(Email,))
            var4=cursor.fetchone()
            cursor = db.execute("select ID from Pacientes where Telemovel=?",(Telemovel,))
            var5=cursor.fetchone()
            cursor = db.execute("select ID from Pacientes where NrCC=?",(NrCC,))
            var6=cursor.fetchone()

            if var1 or var2 or var3 or var4 or var5 or var6:
                app.config["erroGC"] = 1
                return redirect(url_for('GerirConta'))
            else:
                cursor=db.execute("UPDATE Medicos SET Nome=?,Apelido=?,Idade=?,NrCC=?,ID_Especialidade=?,Mail=?,ID_Sexo=?,Telemovel=?,ID_Atividade=1,Info=1 where NIF_Login=?",(Nome,Apelido,Idade,NrCC,Especialidade,Email,Sexo,Telemovel,session['username']))
                db.commit()
                return redirect(url_for('Portal'))
        else:
            MedicoAssociado = request.form['MedicoAssociado']

            cursor = db.execute("select ID from Medicos where Mail=? and NIF_Login<>?",(Email,))
            var1=cursor.fetchone()
            cursor = db.execute("select ID from Medicos where Telemovel=? and NIF_Login<>?",(Telemovel,))
            var2=cursor.fetchone()
            cursor = db.execute("select ID from Medicos where NrCC=? ",(NrCC,))
            var3=cursor.fetchone()
            cursor = db.execute("select ID from Pacientes where Email=? and NIF<>?",(Email,session['username']))
            var4=cursor.fetchone()
            cursor = db.execute("select ID from Pacientes where Telemovel=? and NIF<>?",(Telemovel,session['username']))
            var5=cursor.fetchone()
            cursor = db.execute("select ID from Pacientes where NrCC=? and NIF<>?",(NrCC,session['username']))
            var6=cursor.fetchone()

            if var1 or var2 or var3 or var4 or var5 or var6:
                app.config["erroGC"] = 1
                return redirect(url_for('GerirConta'))
            else:
                cursor=db.execute("UPDATE Pacientes SET Nome=?,Apelido=?,Idade=?,NrCC=?,ID_Sexo=?,Telemovel=?,ID_Medico=?,Email=?,ID_Atividade=1,Info=1 where NIF=?",(Nome,Apelido,Idade,NrCC,Sexo,Telemovel,MedicoAssociado,Email,session['username']))
                db.commit()
                return redirect(url_for('Portal'))
            

    db=get_db()
    cursor=db.execute("SELECT * FROM Sexo")
    ListaSexo = cursor.fetchall()
    cursor=db.execute("SELECT ID,Nome,Apelido FROM Medicos where Info=1")
    ListaMedicos = cursor.fetchall()
    cursor=db.execute("SELECT * FROM Especialidade")
    ListaEspecialidade = cursor.fetchall()

    ListaNotifics = app.config.get("Notificações")

    if session['Funcao']==2:
        cursor=db.execute("select Info from Medicos where NIF_Login=?",(session['username'],))
        result=cursor.fetchone()
        Info=str(result[0])

        if Info=='0':
            Dados={
                "Nome": "",
                "Apelido": "",
                "Sexo": "",
                "Idade": "",
                "E-mail": "",
                "Telemovel": "",
                "CC": "",
                "Especialidade": ""
            }

        else:
            cursor=db.execute("select Nome,Apelido,Idade,ID_Especialidade,Mail,ID_Sexo,Telemovel,NrCC from Medicos where NIF_Login=?",(session['username'],))
            Dados=cursor.fetchone()

            Dados={
                "Nome": Dados[0],
                "Apelido": Dados[1],
                "Sexo": Dados[5],
                "Idade": Dados[2],
                "E-mail": Dados[4],
                "Telemovel": Dados[6],
                "CC": Dados[7],
                "Especialidade": Dados[3]
            }
            
    else:

        cursor=db.execute("select Info from Pacientes where NIF=?",(session['username'],))
        result=cursor.fetchone()
        Info=str(result[0])

        if Info=='0':
            Dados={
                "Nome": "",
                "Apelido": "",
                "Sexo": "",
                "Idade": "",
                "E-mail": "",
                "Telemovel": "",
                "CC": "",
                "Medico": ""
            }
        else:
            cursor=db.execute("select Nome,Apelido,Idade,Email,ID_Sexo,Telemovel,NrCC,ID_Medico from Pacientes where NIF=?",(session['username'],))
            Dados=cursor.fetchone()

            Dados={
                "Nome": Dados[0],
                "Apelido": Dados[1],
                "Sexo": Dados[4],
                "Idade": Dados[2],
                "E-mail": Dados[3],
                "Telemovel": Dados[5],
                "CC": Dados[6],
                "Medico": Dados[7]
            }
            
    if app.config.get("erroGC")==1:
        app.config["erroGC"]=0
        return render_template('GerirConta.html',ListaNotifics=ListaNotifics,Funcao=session['Funcao'],ListaSexo=ListaSexo,ListaMedicos=ListaMedicos,ListaEspecialidade=ListaEspecialidade,Dados=Dados,erro="Os dados que inseriu não são válidos no sistema.")
    else:
        return render_template('GerirConta.html',ListaNotifics=ListaNotifics,Funcao=session['Funcao'],ListaSexo=ListaSexo,ListaMedicos=ListaMedicos,ListaEspecialidade=ListaEspecialidade,Dados=Dados)

@app.route("/Estatisticas",methods=['GET','POST'])
def Estatisticas():
    if request.method=="POST":
        return redirect(url_for('Portal'))
    else:
        db=get_db()
        cursor = db.execute("select avg(P.Idade),avg(M.Idade) from Pacientes P join Medicos M where M.ID_Atividade=1 and P.ID_Atividade=1")
        idades=cursor.fetchone()
        MediaIdadeP = idades[0]
        MediaIdadeM = idades[1]

        cursor = db.execute("select count(*) from Pacientes where ID_Atividade=1")
        var=cursor.fetchone()
        PacientesAtivos = var[0]

        cursor = db.execute("select count(*) from Medicos where ID_Atividade=1")
        var=cursor.fetchone()
        MedicosAtivos = var[0]

        
        cursor = db.execute("select count(ID) from Pacientes where ID_Atividade=1;")
        var=cursor.fetchone()
        var1 = var[0]
        cursor = db.execute("select count(ID) from Medicos where ID_Atividade=1;")
        var=cursor.fetchone()
        var2 = var[0]

        cursor = db.execute("select count(login) from login where ID!=1")
        var=cursor.fetchone()
        var3 = var[0]


        ativos = float(var1)+float(var2)
        PercentagemInativos = round(float(100 - ((ativos)/float(var3))*100),2)

        cursor = db.execute("select count(ID) from Marcacao where ID_Evento=2")
        var=cursor.fetchone()
        ConMarcadas = var[0]

        cursor = db.execute("select count(ID) from Marcacao where ID_Evento=2 and ID_Presenca=1")
        var=cursor.fetchone()
        ConEfetuadas = var[0]

        cursor = db.execute("select count(ID) from Marcacao where ID_Evento=1")
        var=cursor.fetchone()
        ExamMarcadas = var[0]

        cursor = db.execute("select count(ID) from Exames")
        var=cursor.fetchone()
        ExamEfetuados = var[0]

        cursor = db.execute("select count(ID) from Exames where Anotacoes not null")
        var=cursor.fetchone()
        ExamANotados = var[0]

        Estatisticas = {
            "MediaIdadeP":int(MediaIdadeP),
            "MediaIdadeM":int(MediaIdadeM),
            "PacientesAtivos":PacientesAtivos,
            "MedicosAtivos":MedicosAtivos,
            "ApenasRegisto":PercentagemInativos,
            "ConMarcadas":ConMarcadas,
            "ConEfetuadas":ConEfetuadas,
            "PercentCons":round((float(ConEfetuadas)/float(ConMarcadas))*100,2),
            "ExamMarcadas":ExamMarcadas,
            "ExamEfetuados":ExamEfetuados,
            "PercentExams":round((float(ExamEfetuados)/float(ExamMarcadas))*100,2),
            "ExamANotados":ExamANotados
        }
        ListaNotifics = app.config.get("Notificações")

        return render_template("Estatisticas.html",ListaNotifics=ListaNotifics,Estatisticas=Estatisticas)
    

@app.route("/Mensagens",methods=['GET','POST'])
def Mensagens():
    if request.method=='POST':
        db=get_db()
        Mensagem = request.form.get('message')
        Hora = request.form.get('currentTime')
        Data = request.form.get('currentDateFormatted')
        Destinatario = request.form.get('recipient')
        cursor=db.execute("insert into Mensagens(NIF_Emissor,NIF_Destinatario,Data,Hora,ConteudoMensagem,Estado) values(?,?,?,?,?,'Não Lida')",(session['username'],Destinatario,Data,Hora,Mensagem))
        db.commit()
    
    ListaNotifics = app.config.get("Notificações")
    Funcao=session['Funcao']

    if Funcao==2:
        db=get_db()
        cursor=db.execute("select Info from Medicos where NIF_Login=?",(session['username'],))
        result=cursor.fetchone()
        Info=str(result[0])
    elif Funcao==3:
        db=get_db()
        cursor=db.execute("select Info from Pacientes where NIF=?",(session['username'],))
        result=cursor.fetchone()
        Info=str(result[0])
    else:
        Info='1'

    if Info=='1':
        db=get_db()
        if Funcao==1:
            cursor=db.execute("select NIF,Nome,Apelido from Admins where NIF!=?",(session['username'],))
            listaContactos = cursor.fetchall()
        elif Funcao==2:
            cursor = db.execute("select ID from Medicos where NIF_Login=?",(session['username'],))
            ID = cursor.fetchone()
            ID=ID[0]
            cursor=db.execute("SELECT NIF, P.Nome, P.Apelido FROM Pacientes AS P INNER JOIN Medicos AS M ON P.ID_Medico = M.ID WHERE M.ID <> ? OR (M.ID = ? AND P.ID_Medico IS NOT NULL)",(ID,ID))
            listaContactos = cursor.fetchall()
        else:
            cursor = db.execute("select ID_Medico from Pacientes where NIF=?",((session['username'],)))
            IDMedico = cursor.fetchone()
            IDMedico=IDMedico[0]
            cursor=db.execute("SELECT NIF_Login,m.Nome,m.Apelido FROM Medicos m JOIN Pacientes p ON m.ID = p.ID_Medico WHERE p.ID_Medico = ? and p.NIF=?",(IDMedico,session['username']))
            listaContactos1 = cursor.fetchall()

            listaContactos=[]
            for linha in listaContactos1:
                dados = {
                    "NIF": linha[0],
                    "Nome": linha[1],
                    "Apelido": linha[2]
                }
                listaContactos.append(dados)
        #cursor = db.execute("SELECT NIF_Emissor, Data, Hora, ConteudoMensagem FROM Mensagens WHERE NIF_Emissor = ? OR NIF_Destinatario = ? ORDER BY Data, Hora", (session['username'], session['username']))
        #mensagens = cursor.fetchall()

        recipient = request.args.get('recipient')

        if recipient:
            cursor=db.execute("SELECT NIF_Emissor, NIF_Destinatario, Data, Hora, ConteudoMensagem FROM Mensagens WHERE (NIF_Emissor = ? AND NIF_Destinatario = ?) OR (NIF_Emissor = ? AND NIF_Destinatario = ?)",(session['username'],recipient,recipient,session['username']))
            mensagens=cursor.fetchall()

            # Lista para armazenar as mensagens formatadas
            formatted_messages = []
            for item in mensagens:
                dados = {
                    "Emissor": item[0],
                    "Destinatario": item[1],
                    "Data": item[2],
                    "Hora": item[3],
                    "Conteudo": item[4]
                }
                formatted_messages.append(dados)


            mensagens_formatadas={"Mensagens": formatted_messages}
        # Iterar sobre as mensagens do cursor e formatá-las
        #subpasta = 'templates'
        #caminho_arquivo = os.path.join(subpasta, 'formatted_messages.json')

        # Supondo que formatted_messages seja uma lista de dicionários
        #with open(caminho_arquivo, 'w') as json_file:
        #    json.dump(formatted_messages, json_file)
        
            db=get_db()
            cursor=db.execute("update Mensagens set Estado='Lida' where NIF_Destinatario = ?",(session['username'],))
            db.commit()
            db.close()
            return jsonify(mensagens_formatadas)
            #return render_template("Mensagens.html",Mensagens=formatted_messages,recipient=recipient,Funcao=Funcao,Contactos=listaContactos,user=session['username'])
        else:
            return render_template("Mensagens.html",ListaNotifics=ListaNotifics,Funcao=Funcao,Contactos=listaContactos,user=session['username'])
    else:
        return render_template("Mensagens.html",mensagem="Para aceder à caixa de entrada, é necessário regularizar a sua conta. Aceda a 'Gerir Conta' e atualize a informação, por favor.")

@app.route("/guardar_informacoes",methods=['GET','POST'])
def guardarMarcacoes():
    if request.method=='POST':
        db=get_db()
        data = str(request.form.get('data'))
        tipo = str(request.form.get('tipo'))
        paciente = str(request.form.get('paciente'))
        hora = str(request.form.get('hora'))

        data = data.replace("/", "-")
        dte = data +" "+ hora

        dte_final = dt.datetime.strptime(dte, "%d-%m-%Y %H:%M")
        sqlite_datetime = dte_final.strftime("%Y-%m-%d %H:%M:%S")

        cursor = db.execute("select ID from Evento where Descricao=?",(tipo,))
        tipo_row = cursor.fetchone()
        if tipo_row:
            tipo = tipo_row[0]  # Obtém o valor da primeira coluna da linha
        cursor = db.execute("select ID from Medicos where NIF_Login=?",(session['username'],))
        
        medico_row = cursor.fetchone()
        if medico_row:
            medico = medico_row[0]  # Obtém o valor da primeira coluna da linha

        cursor=db.execute("insert into Marcacao(ID_Medico,ID_Paciente,ID_Evento,Dte) values(?,?,?,?)",(medico,paciente,tipo,sqlite_datetime))
        db.commit()
        return redirect(url_for('Portal'))

@app.route("/guardar_pedido",methods=["POST"])
def guardar_pedido():
    if request.method=="POST":
        data = dt.datetime.today().strftime("%d/%m/%Y")
        db=get_db()
        cursor=db.execute("select ID,ID_Medico from Pacientes where NIF=?",(session['username'],))
        lista=cursor.fetchone()
        ID_Paciente=lista[0]
        ID_Medico=lista[1]
        cursor=db.execute("select P.Nome,P.Apelido,M.Nome,M.Apelido from Pacientes P join Medicos M on P.ID_Medico=M.ID where P.ID=?",(int(ID_Paciente),))
        nomes=cursor.fetchone()
        NomeP=nomes[0]
        ApelidoP=nomes[1]
        NomeM=nomes[2]
        ApelidoM=nomes[3]
        NomePaciente = NomeP + ' ' + ApelidoP
        NomeMedico = NomeM + ' ' + ApelidoM
        dados=[]
        dados.append({
            'NomeMedico': NomeMedico,
            'NomePaciente': NomePaciente
        })

        app.config["dados"]=dados
        
        #alterar :
        db = get_db()
        cursor = db.execute("select ID_Medico,ID_Dificuldade,Erro,PercentagemAcerto,Tempo,Data from Exames where ID_Paciente=?",(int(ID_Paciente),))
        examesefetuados = cursor.fetchall()
        DadosExames = []
        x=[]
        y=[]
        cores = []
        tamanho = []
        dificuldades = []

        texto=""
        for item in examesefetuados:
            dados={
                "ID_Medico": item[0],
                "ID_Dificuldade": item[1],
                "Erro": item[2],
                "PercentagemAcerto": item[3],
                "Tempo": item[4],
                "Data": item[5]
            }
            DadosExames.append(dados)
            texto1="<p><b>Data do exame: </b><em>"+item[5]+"</em></p><p><b>Erro: </b><em>"+item[2]+"</em></p><p><b>Percentagem de acerto: </b><em>"+item[3]+" %</em></p><p><b>Tempo decorrido: </b><em>"+item[4]+" s</em></p><br>"
            texto=texto+texto1

            x.append(item[5])
            y.append(float(item[3]))
            if float(item[2])<250:
                size = 1.2 * float(item[2])
                tamanho.append(size)
            elif (float(item[2])>=250) and (float(item[2])<500):
                size = 1.2 * float(item[2])
                tamanho.append(size)
            else:
                size = 1.2 * float(item[2])
                tamanho.append(size)
            
            if item[1] == 1:
                cores.append('green')
                dificuldades.append('Facil')
            elif item[1] == 2:
                cores.append('yellow')
                dificuldades.append('Medio')
            else:
                cores.append('red')
                dificuldades.append('Dificil')

        cursor=db.execute("select Nome,Apelido,Idade from Pacientes where ID=?",(int(ID_Paciente),))
        pac = cursor.fetchone()
        DadosPaciente = {
            "ID":(int(ID_Paciente),),
            "Nome":pac[0],
            "Apelido":pac[1],
            "Idade":pac[2]
        }
        plt.style.use('seaborn-v0_8-dark-palette')
        
        fig, ax = plt.subplots()

        scatter = ax.scatter(x,y,marker="o",s=tamanho,edgecolors="black",c=cores)
        
        plt.grid

        plt.xlabel("Data")
        plt.ylabel("% Acerto")
        plt.ylim(0,100)

        plt.savefig('static/grafico.png')

        #alterar:
        db=get_db()
        cursor=db.execute("select Email from Pacientes where NIF=?",(session['username'],))
        recipient=cursor.fetchone()
        recipient=recipient[0]
        
        x=("Portal NeuroDraw",'neurodrawpt@gmail.com')

        message = Message(
            subject='Envio de relatório',
            recipients=[recipient],
            sender=x
        )
        
        message.html='<h1>Obrigado por utilizar o NeuroDraw, '+NomePaciente+'!</h1><p>Uma vez que pediu o seu relatório médico,...      este e-mail serve como tal e pedimos que não responda.</p><br><p>De seguida encontram-se os dados de todos os exames realizados até hoje:</p>'+texto+'<p>Em anexo encontra-se o gráfico de <em>follow-up</em> dos exames realizados até ao momento.</p><p>Com os melhores cumprimentos,</p><p><em>A Equipa do <b>NeuroDraw</b></p></em>'
        message.attach("../static/grafico.png","grafico/png",app.open_resource("static/grafico.png").read())
        mail.send(message)

        
        return redirect(url_for('Portal'))


@app.route("/guardar_presenca",methods=["GET","POST"])
def guardar_presenca():
    if request.method=="POST":
        idPaciente = str(request.form.get('idPaciente'))
        idPresenca = str(request.form.get('idPresenca'))
        idMarcacao = str(request.form.get('idMarcacao'))

        db=get_db()
        cursor = db.execute("update Marcacao set ID_Presenca=? where ID=? and ID_Paciente=?",(idPresenca,idMarcacao,idPaciente))
        db.commit()
        db.close()
        return redirect(url_for('Portal'))



@app.route("/FazerExame",methods=["GET","POST"]) 
def FazerExame():
    if request.method=='GET':
        ListaNotifics = app.config.get('Notificações')
        return render_template('FazerExame.html',ListaNotifics=ListaNotifics,etapa=1)
    else:
        ListaNotifics = app.config.get('Notificações')
        Dificuldade=app.config.get('Dificuldade')
        BotaoEscolhido=request.form["BotaoEscolhido"]
        if BotaoEscolhido == "submeter":
            Parar = app.config.get('Parar')
            ciclo = app.config.get('ciclo')
            if Parar == 1 and ciclo>0:
                db=get_db()
                cursor=db.execute("select ID,Nome,Apelido,Idade from Pacientes where NIF=?",((session['username'],)))
                listaInfo=cursor.fetchone()
                ID = listaInfo[0]
                Nome = listaInfo[1]
                Apelido = listaInfo[2]
                Idade = listaInfo[3]

                NomePessoa=Nome+' '+Apelido

                erroQuadraticoMedioTotal = app.config.get('erroQuadraticoMedioTotal')
                mascara6 = app.config.get('mascara6')
                mascara5 = app.config.get('mascara5')
                mascara3 = app.config.get('mascara3')
                DATA = app.config.get('DATA')
                segundos = app.config.get('segundos')

                erroQuadraticoMedioTotal = erroQuadraticoMedioTotal/ciclo
                erroQuadraticoMedioTotal = round(erroQuadraticoMedioTotal,2)
                PercentagemAcerto = (np.sum(mascara6&mascara3)/np.sum(mascara3))*100
                PercentagemAcerto = round(PercentagemAcerto,2)
                dia = dt.datetime.today().day
                mes = dt.datetime.today().month
                ano = dt.datetime.today().year
                NomeFicheiro = str(ID) + '_' + str(Nome) + '_' + str(Dificuldade) +'_'+ str(dia) +'_'+ str(mes) +'_'+ str(ano) +  '.jpg' #nome do ficheiro jpg
                cv2.putText(mascara5, f"MSE: {str(erroQuadraticoMedioTotal)} ", (25,400), cv2.FONT_HERSHEY_TRIPLEX, 0.6, (255,255,255), 1)  #vai escrever  o valor do erro Percentual quando o ficheiro for guardado // Sintaxe: cv2.putText(image, text, org, font, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]]) -> https://www.geeksforgeeks.org/python-opencv-cv2-puttext-method/ 
                cv2.putText(mascara5, f"Idade: {str(Idade)} anos", (25,50), cv2.FONT_HERSHEY_TRIPLEX, 0.6, (255,255,255), 1)  #vai escrever  o valor do erro Percentual quando o ficheiro for guardado // Sintaxe: cv2.putText(image, text, org, font, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]]) -> https://www.geeksforgeeks.org/python-opencv-cv2-puttext-method/ 
                cv2.putText(mascara5, f"ID Paciente: {str(ID)} ", (220,50), cv2.FONT_HERSHEY_TRIPLEX, 0.6, (255,255,255), 1)  #vai escrever  o valor do erro Percentual quando o ficheiro for guardado // Sintaxe: cv2.putText(image, text, org, font, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]]) -> https://www.geeksforgeeks.org/python-opencv-cv2-puttext-method/ 
                cv2.putText(mascara5, f"Dificuldade: {str(Dificuldade)} ", (400,50), cv2.FONT_HERSHEY_TRIPLEX, 0.6, (255,255,255), 1)  #vai escrever  o valor do erro Percentual quando o ficheiro for guardado // Sintaxe: cv2.putText(image, text, org, font, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]]) -> https://www.geeksforgeeks.org/python-opencv-cv2-puttext-method/ 
                cv2.putText(mascara5, f"Desenho: ", (25,120), cv2.FONT_HERSHEY_TRIPLEX, 0.6, (255,255,255), 1)  #vai escrever  o valor do erro Percentual quando o ficheiro for guardado // Sintaxe: cv2.putText(image, text, org, font, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]]) -> https://www.geeksforgeeks.org/python-opencv-cv2-puttext-method/ 
                cv2.putText(mascara5, f"Tempo: {str(segundos)} s", (350,400), cv2.FONT_HERSHEY_TRIPLEX, 0.6, (255,255,255), 1)  #vai escrever  o valor do erro Percentual quando o ficheiro for guardado // Sintaxe: cv2.putText(image, text, org, font, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]]) -> https://www.geeksforgeeks.org/python-opencv-cv2-puttext-method/ 
                cv2.putText(mascara5, f"Acerto: {str(PercentagemAcerto)} %", (350,430), cv2.FONT_HERSHEY_TRIPLEX, 0.6, (255,255,255), 1)  #vai escrever  o valor do erro Percentual quando o ficheiro for guardado // Sintaxe: cv2.putText(image, text, org, font, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]]) -> https://www.geeksforgeeks.org/python-opencv-cv2-puttext-method/                             
                cv2.putText(mascara5, f"Data: {str(DATA)}", (350,460), cv2.FONT_HERSHEY_TRIPLEX, 0.6, (255,255,255), 1)  #vai escrever  o valor do erro Percentual quando o ficheiro for guardado // Sintaxe: cv2.putText(image, text, org, font, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]]) -> https://www.geeksforgeeks.org/python-opencv-cv2-puttext-method/                                         
                cv2.circle(mascara5,(50,425),5,(0,255,0),-1)
                cv2.putText(mascara5, "MSE < 50", (57,428), cv2.FONT_HERSHEY_TRIPLEX, 0.3, (255,255,255), 1)  #vai escrever  o valor do erro Percentual quando o ficheiro for guardado // Sintaxe: cv2.putText(image, text, org, font, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]]) -> https://www.geeksforgeeks.org/python-opencv-cv2-puttext-method/ 
                cv2.circle(mascara5,(50,445),5,(0,255,255),-1)
                cv2.putText(mascara5, "50 =< MSE < 70", (57,448), cv2.FONT_HERSHEY_TRIPLEX, 0.3, (255,255,255), 1)  #vai escrever  o valor do erro Percentual quando o ficheiro for guardado // Sintaxe: cv2.putText(image, text, org, font, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]]) -> https://www.geeksforgeeks.org/python-opencv-cv2-puttext-method/ 
                cv2.circle(mascara5,(50,465),5,(0,0,255),-1)
                cv2.putText(mascara5, "MSE >= 70", (57,468), cv2.FONT_HERSHEY_TRIPLEX, 0.3, (255,255,255), 1)  #vai escrever  o valor do erro Percentual quando o ficheiro for guardado // Sintaxe: cv2.putText(image, text, org, font, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]]) -> https://www.geeksforgeeks.org/python-opencv-cv2-puttext-method/ 

                app.config['mascara5']=mascara5
                app.config['erroQuadraticoMedioTotal'] = erroQuadraticoMedioTotal
                app.config['PercentagemAcerto'] = PercentagemAcerto
                app.config['DATA'] = str(DATA)


                #FicheiroExcel_folha = pd.read_excel("Resultados.xlsx") #abre o Excel da pasta
                diretorio = "static/examesProvisorios/"+NomeFicheiro
                cv2.imwrite(diretorio, mascara5) #cria o ficheiro jpg -> https://www.geeksforgeeks.org/python-opencv-cv2-imwrite-method/
                app.config['NomeFicheiro']=NomeFicheiro
                video.release() #Pára a captura de video
                return redirect(url_for('ReverExame'))
            else:
                return render_template('FazerExame.html',ListaNotifics=ListaNotifics,erro="O exame não se encontrava finalizado. Por favor, tente novamente.")
        elif BotaoEscolhido == "mudar":
            return render_template('FazerExame.html',ListaNotifics=ListaNotifics,etapa=1)
        elif BotaoEscolhido == "limpar":
            return render_template('FazerExame.html',ListaNotifics=ListaNotifics)
        else:
            app.config['Dificuldade'] = BotaoEscolhido
            return render_template('FazerExame.html',ListaNotifics=ListaNotifics)

@app.route('/video_feed')
def video_feed():
    db=get_db()
    cursor=db.execute("select ID,Nome,Apelido,Idade,ID_Medico from Pacientes where NIF=?",((session['username'],)))
    listaInfo=cursor.fetchone()
    ID = listaInfo[0]
    Nome = listaInfo[1]
    Apelido = listaInfo[2]
    Idade = listaInfo[3]
    app.config['ID_Medico']=listaInfo[4]
    app.config['ID_Paciente']=ID

    NomePessoa=Nome+' '+Apelido

    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/ReverExame",methods=["GET","POST"])
def ReverExame():
    if request.method=='POST':
        BotaoEscolhido=request.form['BotaoEscolhido']
        if BotaoEscolhido=='cancelar':
            return redirect(url_for('FazerExame'))
        else:
            NomeFicheiro=app.config.get('NomeFicheiro')
            mascara5 = app.config.get('mascara5')
            
            diretorio = "static/examesDefinitivos/"+NomeFicheiro
            cv2.imwrite(diretorio,mascara5)


            ID_Paciente=app.config.get('ID_Paciente')
            Dificuldade=app.config.get('Dificuldade')
            if Dificuldade=='Facil':
                Dificuldade=1
            elif Dificuldade=='Medio':
                Dificuldade=2
            else:
                Dificuldade=3

            ID_Medico=app.config.get('ID_Medico')
            erro=app.config.get('erroQuadraticoMedioTotal')
            acerto=app.config.get('PercentagemAcerto')
            tempo=app.config.get('segundos')
            data=app.config.get('DATA')
            
            Dte = dt.datetime.today().strftime("%Y-%m-%d")
            db = get_db()
            cursor=db.execute("select ID from Marcacao where ID_Medico=? and ID_Paciente=? and ID_Evento='1' and  strftime('%Y-%m-%d', Dte) = ?",(ID_Medico,ID_Paciente,Dte))
            ID_Marcacao=cursor.fetchone()
            ID_Marcacao=ID_Marcacao[0]
            cursor = db.execute("insert into Exames(ID_Medico,ID_Paciente,ID_Dificuldade,Erro,PercentagemAcerto,Tempo,Data,ID_Marcacao,Ficheiro) values(?,?,?,?,?,?,?,?,?)",(ID_Medico,ID_Paciente,Dificuldade,erro,acerto,tempo,data,ID_Marcacao,diretorio))
            db.commit()
            db.close()
            return redirect(url_for('Portal'))
    else:
        NomeFicheiro = app.config.get('NomeFicheiro')
        ListaNotifics=app.config.get('Notificações')
        return render_template("ReverExame.html",NomeFicheiro=NomeFicheiro,ListaNotifics=ListaNotifics)
    
@app.route("/VerExame",methods=["GET","POST"])
def VerExame():
    if request.method=="POST":
        id = app.config.get('IDPaciente')  # Obtenha o ID enviado
        data=app.config.get('DataExame')
        texto=request.form["fname"]
        db=get_db()
        cursor=db.execute("update Exames set Anotacoes=? where ID=?",(texto,data))
        db.commit()
        db.close()
        app.config["varAux"]=1
        return redirect(url_for('VerExame'))
    else:
        if app.config.get("varAux")==1:
            app.config["varAux"]=0
            id = app.config.get('IDPaciente')  # Obtenha o ID enviado
            data=app.config.get('DataExame')
            app.config["IDPaciente"]=id
            app.config["DataExame"]=data
            db=get_db()
            cursor=db.execute("select ID,Data from Exames where ID_Paciente=?",id)
            listaExamesFeitos=cursor.fetchall()   
        else:
            id = request.args.get('id')  # Obtenha o ID enviado
            data=request.args.get('data')
            app.config["IDPaciente"]=id
            app.config["DataExame"]=data
            db=get_db()
            cursor=db.execute("select ID,Data from Exames where ID_Paciente=?",id)
            listaExamesFeitos=cursor.fetchall()
    
        app.config["varAux"]=0
        listaExames=[]
        for item in listaExamesFeitos:
            dados = {
                "ID":item[0],
                "Data":item[1]
            }
            listaExames.append(dados)
        # Faça o que quiser com o ID recebido para "/VerExame"
        ListaNotifics=app.config.get('Notificações')
        if data=="0":
            return render_template("VerExame.html",ListaNotifics=ListaNotifics,id=id,idpessoa=id,ListaDatas=listaExames,mensagem="Por favor, selecione uma data disponível.")
        else:
            db=get_db()
            cursor=db.execute("select ID_Dificuldade,Erro,PercentagemAcerto,Tempo,Ficheiro,Anotacoes from Exames where ID=?",data)
            listaDados=cursor.fetchall()

            Dados=[]
            for item in listaDados:
                dados = {
                    "ID_Dificuldade":item[0],
                    "Erro":item[1],
                    "PercentagemAcerto":item[2],
                    "Tempo":item[3],
                    "Ficheiro":item[4],
                    "Anotacoes":item[5]
                }
                Dados.append(dados)
            return render_template("VerExame.html",ListaNotifics=ListaNotifics,id=id,idpessoa=id,ListaDatas=listaExames,ListaDados=listaDados)        
        
@app.route("/InfoPacientes",methods=["GET","POST"])
def InfoPacientes():
    if request.method=="POST":
        return redirect(url_for('Portal'))
    
    id = request.args.get('id')  # Obtenha o ID enviado
    db = get_db()
    cursor=db.execute("select Nome,Apelido,Idade,ID_Sexo,Telemovel,Email from Pacientes where ID=?",id)
    lista=cursor.fetchone()
    lista={
        "Nome": lista[0],
        "Apelido": lista[1],
        "Sexo": lista[3],
        "Idade": lista[2],
        "E-mail": lista[5],
        "Telemovel": lista[4]
    }

    ListaNotifics=app.config.get('Notificações')
    return render_template("InfoPacientes.html",ListaNotifics=ListaNotifics,ListaInformacoes=lista,id=id)

@app.route("/verInfo",methods=["GET","POST"])
def verInfo():
    if request.method=="POST":
        return redirect(url_for('Portal'))
    else:
        id = request.args.get('id')  # Obtenha o ID enviado
        tipo = request.args.get('tipo')
        db = get_db()
        if tipo=="Médico":
            cursor=db.execute("select Nome,Apelido,Idade,ID_Sexo,Telemovel,Mail from Medicos where ID=?",id)
            lista=cursor.fetchone()
            lista={
                "Nome": lista[0],
                "Apelido": lista[1],
                "Sexo": lista[3],
                "Idade": lista[2],
                "E-mail": lista[5],
                "Telemovel": lista[4]
            }
        elif tipo=="Paciente":
            cursor=db.execute("select Nome,Apelido,Idade,ID_Sexo,Telemovel,Email from Pacientes where ID=?",id)
            lista=cursor.fetchone()
            lista={
                "Nome": lista[0],
                "Apelido": lista[1],
                "Sexo": lista[3],
                "Idade": lista[2],
                "E-mail": lista[5],
                "Telemovel": lista[4]
            }

        ListaNotifics=app.config.get('Notificações')
        return render_template("verInfo.html",ListaNotifics=ListaNotifics,tipo=tipo,ListaInformacoes=lista,id=id)

@app.route("/desativar",methods=["GET"])
def desativar():
    id = request.args.get('id')  # Obtenha o ID enviado
    tipo = request.args.get('tipo')
    db = get_db()
    if tipo=="Médico":
        cursor=db.execute("update Medicos set ID_Atividade=2 where ID=?",id)
    elif tipo=="Paciente":
        cursor=db.execute("update Pacientes set ID_Atividade=2 where ID=?",id)
        
    db.commit()
    db.close()
    return redirect(url_for('Portal'))

@app.route("/FollowUp", methods=["GET","POST"])
def FollowUp():
    if request.method=="POST":
        return redirect(url_for('Portal'))
    else:
        id = request.args.get('id')
        db = get_db()
        cursor = db.execute("select ID_Medico,ID_Dificuldade,Erro,PercentagemAcerto,Tempo,Data from Exames where ID_Paciente=?",id)
        examesefetuados = cursor.fetchall()
        DadosExames = []
        x=[]
        y=[]
        cores = []
        tamanho = []
        dificuldades = []

        for item in examesefetuados:
            dados={
                "ID_Medico": item[0],
                "ID_Dificuldade": item[1],
                "Erro": item[2],
                "PercentagemAcerto": item[3],
                "Tempo": item[4],
                "Data": item[5]
            }
            DadosExames.append(dados)

            x.append(item[5])
            y.append(float(item[3]))
            if float(item[2])<250:
                size = 1.2 * float(item[2])
                tamanho.append(size)
            elif (float(item[2])>=250) and (float(item[2])<500):
                size = 1.2 * float(item[2])
                tamanho.append(size)
            else:
                size = 1.2 * float(item[2])
                tamanho.append(size)
            
            if item[1] == 1:
                cores.append('green')
                dificuldades.append('Facil')
            elif item[1] == 2:
                cores.append('yellow')
                dificuldades.append('Medio')
            else:
                cores.append('red')
                dificuldades.append('Dificil')

        cursor=db.execute("select Nome,Apelido,Idade from Pacientes where ID=?",id)
        pac = cursor.fetchone()
        DadosPaciente = {
            "ID":id,
            "Nome":pac[0],
            "Apelido":pac[1],
            "Idade":pac[2]
        }
        plt.style.use('seaborn-v0_8-dark-palette')
        
        fig, ax = plt.subplots()

        scatter = ax.scatter(x,y,marker="o",s=tamanho,edgecolors="black",c=cores)
        
        plt.grid

        plt.xlabel("Data")
        plt.ylabel("% Acerto")
        plt.ylim(0,100)

        plt.savefig('static/grafico.png')

        ListaNotifics=app.config.get('Notificações')
        return render_template("followup.html",ListaNotifics=ListaNotifics,id=id,DadosExames=DadosExames,DadosPaciente=DadosPaciente)

@app.route("/EventosAnteriores",methods=["GET","POST"])
def EventosAnteriores():
    if request.method=="POST":
        return redirect(url_for('Portal'))
    
    else:
        db = get_db()
        username=session['username']
        cursor=db.execute("select ID from Medicos where NIF_Login=?",(str(username),))
        result = cursor.fetchone()
        IDMedico = str(result[0])
        cursor=db.execute("select ID,ID_Paciente,ID_Evento,Dte,ID_Presenca from Marcacao where ID_Medico=? AND DATETIME(Dte) < DATETIME('now') order by Dte desc",(IDMedico,))
        ListaMarcacoesPassadas = cursor.fetchall()
        ListaMarcacoes_passadas=[]

        for linha in ListaMarcacoesPassadas:
            Data,Hora = linha[3].split(" ")
            ano,mes,dia = Data.split("-")
            Data = dia+"/"+mes+"/"+ano
            hour,mins,sec = Hora.split(":")
            Hora=hour+":"+mins
            dados_do_exame = {
                "ID":linha[0],
                "ID_Paciente": linha[1],
                "ID_Evento":linha[2],
                "Dia": Data,
                "Hora": Hora,
                "ID_Presenca":linha[4]
            }
            ListaMarcacoes_passadas.append(dados_do_exame)

        ListaNotifics=app.config.get('Notificações')
        id = request.args.get('id')
        tipo = request.args.get('tipo') # se é exame ou consulta
        if id and tipo:
            db = get_db()
            if tipo=='1': #exame
                cursor = db.execute("select ID from Exames where ID_Marcacao=?",(id,))
                Exame=cursor.fetchone()
                if Exame:
                    return render_template("EventosAnteriores.html",ListaNotifics=ListaNotifics,mensagem2="O(a) paciente realizou o exame referido. Pode ser visualizado na aba referente para o efeito.",ListaMarcacoesPassadas=ListaMarcacoes_passadas)
                else:
                    return render_template("EventosAnteriores.html",ListaNotifics=ListaNotifics,mensagem2="O(a) paciente não realizou o exame referido. Algo não correu conforme o esperado.",ListaMarcacoesPassadas=ListaMarcacoes_passadas)

            else: #consulta
                cursor = db.execute("select ID_Presenca from Marcacao where ID=?",(id,))
                Presenca = cursor.fetchone()
                if Presenca:
                    Presenca=Presenca[0]
                    if Presenca==1:               
                        return render_template("EventosAnteriores.html",ListaNotifics=ListaNotifics,mensagem2="O(a) paciente esteve presente na consulta.",ListaMarcacoesPassadas=ListaMarcacoes_passadas)
                    else:
                        return render_template("EventosAnteriores.html",ListaNotifics=ListaNotifics,mensagem2="O(a) paciente não esteve presente na consulta.",ListaMarcacoesPassadas=ListaMarcacoes_passadas)
                else:
                    return render_template("EventosAnteriores.html",ListaNotifics=ListaNotifics,mensagem2="Ocorreu um erro, não existe informação sobre a presença do utente na consulta",ListaMarcacoesPassadas=ListaMarcacoes_passadas)
        else:
            return render_template("EventosAnteriores.html",ListaNotifics=ListaNotifics,mensagem2="Por favor, selecione um evento disponível para que possa obter mais informações.",ListaMarcacoesPassadas=ListaMarcacoes_passadas)


@app.route("/LocalizacaoConsulta",methods=["GET","POST"])
def LocalizacaoConsulta():
    if request.method=="POST":
        return redirect(url_for('Portal'))
    
    else:
        ListaNotifics=app.config.get('Notificações')
        return render_template("LocalizacaoConsulta.html",ListaNotifics=ListaNotifics)


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('Funcao',None)
    db=get_db()
    cursor=db.execute("update login set remember=0")
    db.commit()
    return redirect(url_for('MenuInicial'))  


"""@app.route("/list") 
def list(): 
    return render_template('list.html')

@app.route("/process", methods=['POST']) 
def process(): 
    db = get_db()
    author=request.form['inputName']
    language=request.form['inputLanguage']
    cursor = db.execute("insert into list (language, author)values (?,?)", (language,author))
    db.commit()
    return redirect(url_for('index')) """




#FIM 
if __name__ == "__main__":
    app.run(debug=True)