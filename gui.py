import PySimpleGUI as sg


sg.theme('Black')
defaultFont = ('arial', 15)


def getNickName():

        layout = [

            [sg.Text('Digite o NickName', font= defaultFont)],
            [sg.Input(font= defaultFont, size = 30, key = '-SELLER-')],
            [sg.Button('Consultar', font=defaultFont, size= 30)],
            [sg.Exit(font = defaultFont, size=30)]
            
        ]

        window = sg.Window('Usconnect Analisa Anúncios', layout)
        while True:

            events, values = window.read()
            if events == 'Exit'or events == sg.WIN_CLOSED: break
            elif events == 'Consultar': 
                 
                return values['-SELLER-']

                 
 
        window.close()

def savedPopup(filename): sg.popup(f'Arquivo salvo como "{filename}"')