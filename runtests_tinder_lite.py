import requests
import unittest

class TestStringMethods(unittest.TestCase):


    def test_000_pessoas_retorna_lista(self):
        #se eu acessar a url /pessoas
        r = requests.get('http://localhost:5003/pessoas')
        #vou ter um retorno que deve ser uma lista
        objeto_retornado = r.json()
        self.assertEqual(type(objeto_retornado),type([]))

    '''
    Para o teste seguinte, pode ser util o seguinte exemplo
    de lista de pessoas

    [
        {
            "id": 9, 
            "nome": "maximus"
        }, 
        {
            "id": 3, 
            "nome": "aurelia"
        }
    ]
    '''

    def test_001_adiciona_pessoas(self):
        r_reset = requests.post('http://localhost:5003/reseta')
        #se ainda nao estiver funcionando, 
        #esse reseta acima, nao se preocupe

        #crio fernando, verificando se deu erro
        r = requests.post('http://localhost:5003/pessoas',
                           json={'nome':'fernando','id':1})
        if r.status_code != 200:
            try:
                print('erro',r.json())
            except:
                print("criacao do fernando nao retornou json")
            self.fail("criação do fernando nao deu certo. Cod status:"+str(r.status_code))

        #crio roberto
        r = requests.post('http://localhost:5003/pessoas',json={'nome':'roberto','id':2})
        if r.status_code != 200:
            try:
                print('erro',r.json())
            except:
                print("criacao do roberto nao retornou json")
            self.fail("criação do roberto nao deu certo")

        #pego a lista de pessoas do servidor e vejo se apareceram
        #roberto e fernando
        r_lista = requests.get('http://localhost:5003/pessoas')
        lista_devolvida = r_lista.json()

        achei_fernando = False
        achei_roberto = False
        for dic_pessoa in lista_devolvida:
            if dic_pessoa['nome'] == 'fernando':
                achei_fernando = True
            if dic_pessoa['nome'] == 'roberto':
                achei_roberto = True
        if not achei_fernando:
            self.fail('pessoa fernando nao apareceu na lista de pessoas')
        if not achei_roberto:
            self.fail('pessoa roberto nao apareceu na lista de pessoas')

    #acessando /pessoas/5, vejo só o dicionario da pessoa 5
    def test_002_pessoa_por_id(self):
        r = requests.post('http://localhost:5003/pessoas',
                           json={'nome':'mario','id':20})
        r = requests.get('http://localhost:5003/pessoas/20')
        dicionario_retornado = r.json()
        self.assertEqual(type(dicionario_retornado),type({}))
        self.assertEqual(dicionario_retornado['nome'],'mario')


    #reseta faz o banco de pessoas e de interesses zerar, 
    #ficar vazio
    def test_003_adiciona_e_reseta(self):
        #crio um usuário
        r = requests.post('http://localhost:5003/pessoas',json={'nome':'cicero','id':29})
        #pego a lista de todos os usuários
        r_lista = requests.get('http://localhost:5003/pessoas')
        #essa lista tem que ter pelo menos 1 elemento, que eu 
        #acabei de criar
        self.assertTrue(len(r_lista.json()) > 0)

        #acesso a url reseta
        r_reset = requests.post('http://localhost:5003/reseta')
        #e a url reseta funciona sem reclamar (retorna cod status 200)
        self.assertEqual(r_reset.status_code,200)

        #agora a lista de usuários deve estar vazia
        r_lista_depois = requests.get('http://localhost:5003/pessoas')
        self.assertEqual(len(r_lista_depois.json()),0)
    '''
    começar o tinder em si

    definir url sinalizar_interesse
    executar um PUT em /sinalizar_interesse/9/3/ significa que 9 está interessado(a) em 3

    a idéia da URL é que temos o usuário de id 9 dizendo que tem interesse em conversar com o(a) usuário(a) de id 3.

    Vamos salver e processar esse interesse nos proximos testes.

    Mas, só pra aquecer, vamos fazer a URL validar essas ids.

    Esse teste verifica se a chamada PUT em /sinalizar_interesse/pessoa_a/pessoa_b
    dá erro quando pessoa_a ou pessoa_b nao existe
    voce nao precisa nem pensar ainda como salvar um interesse,
    só dê um erro se alguma das pessoas envolvidas nao existe
    '''
    def test_100_interesse_com_pessoas_validas(self):
        #reseto
        r_reset = requests.post('http://localhost:5003/reseta')

        #crio a pessoa 9
        r = requests.post('http://localhost:5003/pessoas',json={'nome':'maximus','id':9})
        self.assertEqual(r.status_code,200)

        #interesse de 9 para 3 dá erro, pois 3 nao existe ainda
        r = requests.put('http://localhost:5003/sinalizar_interesse/9/3/')
        self.assertEqual(r.status_code,404)

        #interesse de 3 para 9 dá erro, pois 3 nao existe ainda
        r = requests.put('http://localhost:5003/sinalizar_interesse/3/9/')
        self.assertEqual(r.status_code,404)
        
        #agora crio a pessoa 3
        r = requests.post('http://localhost:5003/pessoas',json={'nome':'aurelia','id':3})
        self.assertEqual(r.status_code,200)

        #agora posso marcar interesse de 3 pra 9 e de 9 pra 3 sem problemas
        r = requests.put('http://localhost:5003/sinalizar_interesse/9/3/')
        self.assertEqual(r.status_code,200)
        r = requests.put('http://localhost:5003/sinalizar_interesse/3/9/')
        self.assertEqual(r.status_code,200)

        #esse finalizinho é só uma piada sobre amor proprio que ficou no teste :P
        r = requests.put('http://localhost:5003/sinalizar_interesse/9/9/')
        self.assertEqual(r.status_code,200)

    '''
    Como guardar os interesses?
    
    Eu fiz assim:
    
    database['interesses'] = {}
    colocar uma chave 3 pros interesses do 3, que vao ser uma lista de ids
    por exemplo
    database['interesses'][3]=[9,4,2]
    database['interesses'][2]=[9,3]

    O que isso quer dizer?
    3 se interessa por 9,4,2
    2, por 9 e 3.
    '''

    '''
    Quando uma pessoa A sinaliza interesse por B,
    B aparece na lista de interesses de A

    (a lista de interesse de A estará disponivel em
    /interesses/A, com o verbo GET)
    '''
    def test_100b_consulta_interesse(self):
        #reseto
        r_reset = requests.post('http://localhost:5003/reseta')
        self.assertEqual(r_reset.status_code,200)

        
        #maximus acabou de ser criado, nao tem interesses
        r = requests.post('http://localhost:5003/pessoas',json={'nome':'maximus','id':9})
        self.assertEqual(r.status_code,200)
        r = requests.get('http://localhost:5003/interesses/9')
        self.assertEqual(r.status_code,200)
        lista_interesses = r.json() 
        self.assertEqual(lista_interesses,[])
        
        #crio aurelia
        r = requests.post('http://localhost:5003/pessoas',json={'nome':'aurelia','id':3})
        self.assertEqual(r.status_code,200)
        
        #maximus está interessado em aurélia
        r = requests.put('http://localhost:5003/sinalizar_interesse/9/3/')
        self.assertEqual(r.status_code,200)
        r = requests.get('http://localhost:5003/interesses/9')
        self.assertEqual(r.status_code,200)
        lista_interesses = r.json() 
        self.assertEqual(lista_interesses,[3])

        #crio diana
        r = requests.post('http://localhost:5003/pessoas',json={'nome':'diana','id':30})
        self.assertEqual(r.status_code,200)
        
        #maximus está interessado em diana
        #(veja na URL, estamos marcando interesse de 9 para 30)
        r = requests.put('http://localhost:5003/sinalizar_interesse/9/30/')
        self.assertEqual(r.status_code,200)
        r = requests.get('http://localhost:5003/interesses/9')
        self.assertEqual(r.status_code,200)
        lista_interesses = r.json() 
        #maximus está interessado tanto em diana quanto em aurelia
        #3 aparece na lista
        self.assertIn(3,lista_interesses)
        #30 tb aparece na lista
        self.assertIn(30,lista_interesses)
        #tam da lista é 2
        self.assertEqual(len(lista_interesses),2)
    
    def test_100c_resetar_afeta_interesses(self):
        #reseto
        r_reset = requests.post('http://localhost:5003/reseta')
        self.assertEqual(r_reset.status_code,200)

        
        #maximus acabou de ser criado, nao tem interesses
        r = requests.post('http://localhost:5003/pessoas',json={'nome':'maximus','id':9})
        self.assertEqual(r.status_code,200)
        r = requests.get('http://localhost:5003/interesses/9')
        self.assertEqual(r.status_code,200)
        lista_interesses = r.json() 
        self.assertEqual(lista_interesses,[])
        
        #crio aurelia
        r = requests.post('http://localhost:5003/pessoas',json={'nome':'aurelia','id':3})
        self.assertEqual(r.status_code,200)
        
        #maximus está interessado em aurélia
        r = requests.put('http://localhost:5003/sinalizar_interesse/9/3/')
        self.assertEqual(r.status_code,200)
        r = requests.get('http://localhost:5003/interesses/9')
        self.assertEqual(r.status_code,200)
        lista_interesses = r.json() 
        self.assertEqual(lista_interesses,[3])
        
        #reseto
        r_reset = requests.post('http://localhost:5003/reseta')
        self.assertEqual(r_reset.status_code,200)
        
        #maximus acabou de ser criado, nao tem interesses
        r = requests.post('http://localhost:5003/pessoas',json={'nome':'maximus','id':9})
        self.assertEqual(r.status_code,200)
        r = requests.get('http://localhost:5003/interesses/9')
        self.assertEqual(r.status_code,200)
        lista_interesses = r.json() 
        self.assertEqual(lista_interesses,[])

    
    '''
    Agora vamos fazer os matches

    usuarios tem uma lista de matches, 
    3 só é um match do 9 se 9 está interessado(a) em 3
    e 3 está interessado(a) em 9
    (3 aparece nos matches de 9 se 3 gosta de 9 e 9 gosta de 3)

    Relembrando a estrutura

    database['interesses'] = {}
    colocar uma chave 3 pros interesses do 3, que vao ser uma lista de ids
    por exemplo
    database['interesses'][3]=[9,4,2]
    database['interesses'][2]=[9,3]

    O que isso quer dizer?
    3 se interessa por 9,4,2
    2, por 9 e 3.

    Como o 3 gosta do 2 e o 2 gosta do 3, existe match entre 3 e 2

    Se eu consultar a lista de matches do 3, eu vou ver o 2 (e vice versa)
    '''

    #matches serão acessados em /matches/id_pessoa, com GET

    def test_101_match(self):
        #reseto
        r_reset = requests.post('http://localhost:5003/reseta')
        self.assertEqual(r_reset.status_code,200)

        
        #maximus acabou de ser criado, nao tem matches
        r = requests.post('http://localhost:5003/pessoas',json={'nome':'maximus','id':9})
        self.assertEqual(r.status_code,200)
        r = requests.get('http://localhost:5003/matches/9')
        self.assertEqual(r.status_code,200)
        lista_matches = r.json() 
        self.assertEqual(lista_matches,[])
        
        #crio aurelia
        r = requests.post('http://localhost:5003/pessoas',json={'nome':'aurelia','id':3})
        self.assertEqual(r.status_code,200)
        
        #maximus está interessado em aurélia, mas ainda não é correspondido
        r = requests.put('http://localhost:5003/sinalizar_interesse/9/3/')
        self.assertEqual(r.status_code,200)
        r = requests.get('http://localhost:5003/matches/9')
        self.assertEqual(r.status_code,200)
        lista_matches = r.json() 
        self.assertEqual(lista_matches,[])
        
        
        #agora ele é correspondido por aurelia
        r = requests.put('http://localhost:5003/sinalizar_interesse/3/9/')
        self.assertEqual(r.status_code,200)
        r = requests.get('http://localhost:5003/matches/9')
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json(),[3]) #agora sim aparece o match

        #crio diana
        r = requests.post('http://localhost:5003/pessoas',json={'nome':'diana','id':30})
        self.assertEqual(r.status_code,200)
        
        #maximus está interessado em diana, mas ainda não é correspondido
        #(veja na URL, estamos marcando interesse de 9 para 30)
        r = requests.put('http://localhost:5003/sinalizar_interesse/9/30/')
        self.assertEqual(r.status_code,200)
        r = requests.get('http://localhost:5003/matches/9')
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json(),[3])

        #agora é correspondido
        r = requests.put('http://localhost:5003/sinalizar_interesse/30/9/')
        self.assertEqual(r.status_code,200)
        r = requests.get('http://localhost:5003/matches/9')
        self.assertEqual(r.status_code,200)
        lista_de_matches = r.json()
        #agora maximus tem 2 matches. A ordem nao importa
        self.assertIn(3,lista_de_matches) #id da aurelia
        self.assertIn(30,lista_de_matches) #id da diana

        #aurélia também tem o match
        r = requests.get('http://localhost:5003/matches/3')
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json(),[9])

        #diana também tem o match
        r = requests.get('http://localhost:5003/matches/30')
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json(),[9])

    #consultar matches de uma pessoa que nao existe resulta
    #cod status 404
    def test_101a_match_404(self):
        #reseto
        r_reset = requests.post('http://localhost:5003/reseta')
        self.assertEqual(r_reset.status_code,200)
        
        #nao tem ninguem ainda, devo ter um erro
        r = requests.get('http://localhost:5003/matches/9')
        self.assertEqual(r.status_code,404)

        #crio a pessoa de id 9
        r = requests.post('http://localhost:5003/pessoas',json={'nome':'maximus','id':9})
        self.assertEqual(r.status_code,200)

        #agora funciona
        r = requests.get('http://localhost:5003/matches/9')
        self.assertEqual(r.status_code,200)

        #mas nao para outras pessoas
        r = requests.get('http://localhost:5003/matches/4')
        self.assertEqual(r.status_code,404)


    #uso do verbo delete, na url sinalizar_interesse, para
    #remover um interesse (e o match, se existia um)

    # A gosta B
    # B gosta A -> match
    # B remove gostar A -> match desaparece
    #(mesmo que A ainda goste de B)

    #perceba, DELETE na url sinalizar interesse, 
    #nao no match
    #mas o efeito é visivel no match
    
    def test_102_match_perdido(self):
        #resetei
        r_reset = requests.post('http://localhost:5003/reseta')
        self.assertEqual(r_reset.status_code,200)

        #nenhum usuario tem matches ainda, porque nao existe usuário
        r = requests.get('http://localhost:5003/matches/9')
        self.assertEqual(r.status_code,404)

        #criei o primeiro usuário
        r = requests.post('http://localhost:5003/pessoas',json={'nome':'maximus','id':9})
        self.assertEqual(r.status_code,200)

        #maximus acabou de ser criado, nao tem matches
        r = requests.get('http://localhost:5003/matches/9')
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json(),[])
        
        #crio aurelia
        r = requests.post('http://localhost:5003/pessoas',json={'nome':'aurelia','id':3})
        self.assertEqual(r.status_code,200)
        
        #maximus está interessado em aurélia, mas ainda não é reciproco
        r = requests.put('http://localhost:5003/sinalizar_interesse/9/3/')
        self.assertEqual(r.status_code,200)
        r = requests.get('http://localhost:5003/matches/9')
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json(),[])

        #aurélia tb tem interesse, a lista de matches de maximus contém ela
        r = requests.put('http://localhost:5003/sinalizar_interesse/3/9/')
        self.assertEqual(r.status_code,200)
        r = requests.get('http://localhost:5003/matches/9')
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json(),[3])

        #aurélia perde o interesse, a lista de matches de maximus esvazia
        r = requests.delete('http://localhost:5003/sinalizar_interesse/3/9/')
        self.assertEqual(r.status_code,200)
        #consulto a lista de maximus
        r = requests.get('http://localhost:5003/matches/9')
        self.assertEqual(r.status_code,200)
        #e tem que ser vazia
        self.assertEqual(r.json(),[])

    #o perfil do usuário (ou usuária) ganha duas caracteristicas novas
    #o sexo e quais pessoas ele(a) está buscando
    #maximus = {'nome':'maximus','id':9,'sexo':'homem','buscando':['mulher']}
    def test_103_match_incompativel(self):
        r_reset = requests.post('http://localhost:5003/reseta')
        self.assertEqual(r_reset.status_code,200)
        r = requests.get('http://localhost:5003/matches/9')
        self.assertEqual(r.status_code,404)
        maximus = {'nome':'maximus','id':9,'sexo':'homem','buscando':['mulher']}
        r = requests.post('http://localhost:5003/pessoas',json=maximus)
        self.assertEqual(r.status_code,200)

        #maximus acabou de ser criado, nao tem matches
        r = requests.get('http://localhost:5003/matches/9')
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json(),[])
        
        #crio aurelia
        aurelia = {'nome':'aurelia','id':3,'sexo':'mulher','buscando':['mulher']}
        r = requests.post('http://localhost:5003/pessoas',json=aurelia)
        self.assertEqual(r.status_code,200)

        #maximus está interessado em aurélia
        r = requests.put('http://localhost:5003/sinalizar_interesse/9/3/')
        self.assertEqual(r.status_code,200)
        r = requests.get('http://localhost:5003/matches/9')
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json(),[])

        #aurelia manifesta interesse em maximus, mas isso é incompativel
        #com suas preferências anteriores
        r = requests.put('http://localhost:5003/sinalizar_interesse/3/9/')
        self.assertEqual(r.status_code,400)
        self.assertEqual(r.json()['erro'],'interesse incompativel')
        #esse erro ocorre quando A manifesta interesse em M, 
        #mas A declarou anteriormente que nao tem interesse 
        #em ninguém do sexo de M
        r = requests.get('http://localhost:5003/matches/9')
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json(),[])

    def test_104_match_compativel(self):
        r_reset = requests.post('http://localhost:5003/reseta')
        self.assertEqual(r_reset.status_code,200)
        r = requests.get('http://localhost:5003/matches/9')
        self.assertEqual(r.status_code,404)
        maximus = {'nome':'maximus','id':9,'sexo':'homem','buscando':['homem','mulher']}
        r = requests.post('http://localhost:5003/pessoas',json=maximus)
        self.assertEqual(r.status_code,200)

        #maximus acabou de ser criado, nao tem matches
        r = requests.get('http://localhost:5003/matches/9')
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json(),[])
        
        #crio aurelia
        aurelia = {'nome':'aurelia','id':3,'sexo':'mulher','buscando':['mulher','homem']}
        r = requests.post('http://localhost:5003/pessoas',json=aurelia)
        self.assertEqual(r.status_code,200)

        #maximus está interessado em aurélia
        r = requests.put('http://localhost:5003/sinalizar_interesse/9/3/')
        self.assertEqual(r.status_code,200)
        r = requests.get('http://localhost:5003/matches/9')
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json(),[])

        #aurelia manifesta interesse em maximus
        r = requests.put('http://localhost:5003/sinalizar_interesse/3/9/')
        self.assertEqual(r.status_code,200)
        r = requests.get('http://localhost:5003/matches/9')
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json(),[3])


        





    

    


def runTests():
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestStringMethods)
        unittest.TextTestRunner(verbosity=2,failfast=True).run(suite)


if __name__ == '__main__':
    runTests()
