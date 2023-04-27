import sys
import datetime
import json

# Constantes qui représente une liste d'items transformés en un dict avec les clés étant
# les ids des items, ainsi que le raw json qui a été parsé.
menu = {}
liste_items = {}
all_users = []
def connect_by_parameters(users):
    # On vérifie si l'utilisateur a décidé de se connecter avec des paramètres.
    # S'il n'y a pas exactement trois arguments passés, on peut déjà retourner None.
    if len(sys.argv) != 3:
        return None
    # On fait les mêmes vérification que si l'utilisateur s'était connecté normalement.
    return get_user_data(users, sys.argv[1], sys.argv[2])


def get_item_dict(menu):
    # On crée une liste d'items pour rendre le print de tous les items, ainsi que le print d'un item à un identifiant
    # spécifique plus facile. Ceci va nous sauver de la répétition et de nombreuses lignes de code.
    global liste_items
    def parcourir_menu(menu):
        for key, value in menu.items():
            # Si 'items' est dans le value, alors on va itérer sur la liste d'items et créer un 'corps' pour chaque item.
            if 'items' in value:
                for item in value['items']:
                    liste_items[item['id']] = {
                        'Nom': item['nom'],
                        'Prix': item['prix'],
                        'Disponible': item['disponible']
                    }
            # S'il ne l'est pas, alors on search plus profond.
            else:
                parcourir_menu(value)
    parcourir_menu(menu)
    return

# On lit le fichier json et on le parse.
def get_menu():
    with open("menu.json", mode="r", encoding="UTF-8") as menu_json:
        return json.load(menu_json)

# On lit les utilisateurs du fichier csv.
def get_users():
    global all_users
    with open(file="comptes.csv", mode="r", encoding="UTF-8") as comptes:
        liste_comptes = comptes.readlines()
        for i in range(len(liste_comptes)):
            liste_comptes[i] = liste_comptes[i].split("|")
            for j in range(len(liste_comptes[i])):
                # On clean up les champs de chaque utilisateur en enleant les espaces et les newlines.
                liste_comptes[i][j] =  liste_comptes[i][j].replace(" ", "").replace("\n", "")
        all_users = liste_comptes
    return user_class(liste_comptes)


def user_class(liste_comptes):
    users = []
    # On crée le 'corps' d'un utilisateur, c'est-à-dire, un dict qui va hold tous ses informations.
    for i in range(len(liste_comptes)):
        user = {
            "Matricule": liste_comptes[i][0],
            "Nom": liste_comptes[i][1],
            "Prénom": liste_comptes[i][2],
            "Mot de passe": liste_comptes[i][3],
            "Adresse Courriel": liste_comptes[i][4],
            "Role": liste_comptes[i][5],
            "Actif": liste_comptes[i][6],
        }
        # On crée une liste d'utilisateurs et on la retourne.
        users.append(user)
    return users

def valid_user(matricule, password, users):
    # Si le matricule et le password match avec un de ceux dans la liste d'utilisateurs, on a un utilisateur valide.
    for user in users:
        if user["Matricule"] == matricule and user["Mot de passe"] == password:
                return True
    return False
    
def check_activity(matricule, users):
    # On vérifie si le status de l'utilisateur est actif.
    for user in users:
        if user["Matricule"] == matricule:
            return False if user['Actif'] == "0" else user

def get_user_data( users: dict, matricule = None, password = None):
    # On prend les données de l'utilisateur et on appel les fonctions nécessaires pour vérifier si l'utilisateur est
    # valide et si son compte est actif.
    if not matricule or not password:
        matricule = input("Entrez votre matricule > ")
        password = input("Entrez votre mot de passe > ")
    if valid_user(matricule, password, users) == False:
        print("Erreur lors de la connexion, veuillez réessayer.")
        return False
    user = check_activity(matricule, users)
    if user == False:
        print("Ce compte n'est plus actif. Veuillez contacter les administrateurs pour modifier le statut du compte.")
        return False
        
    return user


def process_requete(requete_string):
    # On prend une requête du user et on la découpe en ses parties principales, le protocole HTTP, ainsi que les informations.
    request_info = requete_string.split(" ")
    if request_info != [""] and "/" in requete_string:
        request_type, infos = request_info[0].upper(), request_info[1].lower()
    else:
        return None
    # Si la longueur du split > 2, alors il faut passer les informations supplémentaires également.
    if len(request_info) > 2:
        return request_type, infos, request_info[2:]
    return request_type, infos, None

def split_info(infos):
    # On split les éléments de la request.
    info_list = infos.split("/")
    info_list.pop(0)
    return info_list

def get_commande_info(command_id, menu):
    commande = None
    # On met tout la manipulation dans un try pour ne pas à se soucier d'erreurs :).
    # S'il y a une erreur, ca va juste sortir de la fonction sans rien faire.
    try:
        with open("commandes.csv", mode="r", encoding="UTF-8") as commandes:
            buffer = commandes.readlines()
            # On set up un flag pour dire quand nous voulons break de la boucle externe
            indice = False
            for i in range(len(buffer)):
                buffer[i] = buffer[i].split(" | ")
                if indice == True:
                    break
                for j in range(len(buffer[i])):
                    buffer[i][j] = buffer[i][j].replace("\n", "")
                    # Puisque le premier élément et le dernier élément possède des espaces supplémentaires
                    # on les enlève.
                    if j == 0 or j == len(buffer[i]) - 1:
                        buffer[i][j] = buffer[i][j].replace(" ", "")
                        # Si on trouve la commande, alors on peut break
                        if buffer[i][j] == command_id:
                            commande = buffer[i]
                            indice = True
                            break

        items_and_quantities = commande[2].split(" ")
        for item in items_and_quantities:
            item_quantity, item_id = item.split("x")
            print(f"Item: {liste_items[int(item_id)]['Nom']} | Quantité: {item_quantity}")
        print(f"Date: {commande[3].strip()}")
        print(f"Total: {commande[-1].strip()}$")
    except:
        return


def analyze_request(request_type, info, info_supplementaire, role, menu, matricule):
    if request_type.upper() == "GET":
        if info[:2] == ["api", "comptes"]:
            if role != "admin":
                print("Vous ne pouvez pas accéder à cette requête.")
                return
            else:
                if info[-1] != "comptes":
                    show_all_users(info[-1])
                else:
                    show_all_users(None)
        if info[:2] == ["api", "commandes"]:
            # Si l'utilisateur demande pour 
            if role != "staff" and role != "admin":
                print("Vous ne possédez pas les permissions nécessaires! ")
                return
            # Si la request est uniquement /api/commandes, on montre toutes les commandes.
            elif len(info) == 2:    
                get_commandes()
        # Si le dernier item dans le request n'est pas 'commandes', alors l'utilisateur demande
        # une commande spécifique. ie. /api/commandes/1
            elif info[-1] != "commandes":
                get_commande_info(info[-1], menu)
        elif info == ["api", "menu", "items"]:
            show_menu()
            return
        if len(info) >= 3:
            if info[0:2] == ["api", "menu"] and info[-1] == "items":
                show_items(menu, info[2])
                return
            elif info[0:3] == ["api", "menu", "items"] and len(info) > 3:
                try:
                    info[-1] = int(info[-1])
                except:
                    return
                else:
                    show_item_info(menu, info[-1])
    elif request_type.upper() == "POST":
        if info == ["api", "commandes"] and len(info_supplementaire) != 0:
            creer_commande(info_supplementaire, matricule, menu)
    elif request_type.upper() == "PUT" and role in ["staff", "admin"]:
        # Ici, on veut s'assurer que l'utilisateur respecte le format de la request.
        if info[0:3] == ["api", "menu", "items"] and isinstance(info[-1], int) and role in ["staff", "admin"]:
            item_id = int(info[-1])
            # Vérification que l'utilisateur a bien respecté le format.
            if "disponible=" not in info_supplementaire[0]:
                return
            else:
                info_supplementaire = info_supplementaire[0].split("=")
                # Si la longueur est de 1, l'utilisateur n'a pas entré de valeur, c'est donc invalide.
                if len(info_supplementaire) == 1:
                    return
                else:
                    nouvelle_dispo = info_supplementaire[1]
                    update_menu(item_id, nouvelle_dispo)
        elif info[:2] == ["api", "comptes"] and info[-1] != "comptes" and info_supplementaire[0] in ["0", "1"] and role == "admin":
            update_account(info[-1], info_supplementaire[0])
                     


def update_account(matricule, info_supplementaire):
    global all_users
    def update_user_file(all_users):
        # On fait ca pour clear le file.
        with open("comptes.csv", mode="w") as user_file:
            pass
        # On peut réécrire le fichier avec les données updatées.
        with open("comptes.csv", mode="a", encoding="UTF-8") as user_file:
            for i in range(len(all_users)):
                user=f"{all_users[i][0]} | {all_users[i][1]} | {all_users[i][2]} | {all_users[i][3]} | {all_users[i][4]} | {all_users[i][5]} | {all_users[i][6]}\n"
                user_file.write(user)
    for i in range(len(all_users)):
        if all_users[i][0] == matricule:
            all_users[i][-1] = info_supplementaire
            update_user_file(all_users)
            return


def get_commandes():
    
    try:
        with open("commandes.csv", mode="r") as commandes:
            buffer = commandes.readlines()
            for i in range(len(buffer)):
                buffer[i] = buffer[i].split(" | ")
                for j in range(len(buffer[i])):
                    buffer[i][j] = buffer[i][j].replace("\n", "")
                    if j == 0 or j == len(buffer[i]) - 1:
                        buffer[i][j] = buffer[i][j].replace(" ", "")

                # Affichage de chaque commande.
            for row in buffer:
                print(f"Id: {row[0]} | Date: {row[3]} | Total: {row[-1]}$")
    except:
        return


def creer_commande(info_de_commande, matricule, menu):
    prices = []
    items = []
    ids = []

    def calculate_price(num_items, prices):
        prix_total = 0
        if prices == []:
            return
        for i in range(len(num_items)):
            prix_total += int(num_items[i]) * prices[i]
        return prix_total

    def write_command(matricule, prix_total, infos, ids):
        # On prend la date et on le format
        date = datetime.datetime.now()
        date_string = date.strftime("%Y-%m-%d")
        try:
            with open("commandes.csv", mode="r", encoding="UTF-8") as commandes:
                if not commandes:
                    return
                data = commandes.readlines()
                if data != []:
                    for i in range(len(data)):
                        data[i] = data[i].split(" | ")
                    command_id = int(data[-1][0].strip())+1
                else:
                    command_id = 1
                commande_info = [f"{str(command_id)} ", matricule, 
                                 " ".join(info_de_commande), date_string, f"{prix_total:.2f} "]
                
                commande_string = " | ".join(commande_info)
        except:
            return
        
        with open("commandes.csv", mode="a", encoding="UTF_8") as commandes:
            commandes.writelines(f"{commande_string}\n")

        return

    # Ici, on crée une liste pour enlever des éléments d'une commande si l'utilisateur entre des ids invalides i.e. 45.
    index_a_enlever = []
    for i in range(len(info_de_commande)):
        num, item_id = info_de_commande[i].split("x")
        ids.append(item_id)
        items.append(num)
        # On met cette opération dans un try|except pour le cas qu'un index est trop grand.
        try:
            prices.append(liste_items[int(item_id)]["Prix"])
        except:
            ids.pop()
            items.pop()
            index_a_enlever.append(i)
            continue
    # Si l'utilisateur à entré des items invalides, on les enlèves.        
    if index_a_enlever != []:
        for index in index_a_enlever:
            info_de_commande.pop(index)

    prix_total = calculate_price(items, prices)
    # Si le prix total == None, alors l'utilisateur a passé une commande invalide, donc on return.
    if prix_total == None:
        return
    write_command(matricule, prix_total, items, info_de_commande)





def get_requete():
    # On obtient la requête de l'utilisateur et on process cette requête.
    requete = input("")
    requete_processed = process_requete(requete)
    if requete_processed != None:
        request_type, info, info_supplementaire = requete_processed
        info = split_info(info)
        return request_type, info, info_supplementaire
    return "Error", None, None

def show_item_info(menu, item_id):
    try:
        item = liste_items[item_id]
    except:
        return
    else:
        print(f"ID: {item_id} | Nom: {item['Nom']} | Prix: {item['Prix']}$ | Disponibilité: {'Oui' if item['Disponible'] == True else 'Non'}")

def show_items(menu, categorie):
    # Ici, on a vraiment besoin de définir une fonction pour parcourir récursivement le menu à cause des 
    # sous-catégories.
    def parcourir_menu(menu, categorie):
        for key, value in menu.items():
            # Si on trouve la catégorie passée.
            if key == categorie:
                # Juste pour s'assurer qu'on aille pas d'erreur.
                if isinstance(value, list) == False:
                    if 'items' in value:
                        for item in value['items']:
                            print(f"{item['id']} | {item['nom']}")
                        return
                    # Ici, si on trouve une clé qui possède des sous-catégories (i.e. viennoisserie), on explore ces sous-catégories.
                    for clé, valeur in value.items():
                        if 'items' in valeur:
                            for item in valeur['items']:
                                print(f"{item['id']} | {item['nom']}")
                        else:
                            parcourir_menu(valeur, clé)
            # Si on ne trouve pas la catégorie, mais que la valeur associé la clé est une liste, on ne veut pas chercher plus loin
            # donc on return.         
            elif isinstance(value, list):
                return
            # Comme on peut avoir des sous-catégories, alors nous devons chercher plus loin jusqu'à ce que la valeur soit une liste.
            else:
                parcourir_menu(value, categorie)
    parcourir_menu(menu, categorie)

def show_menu():
    for key, value in liste_items.items():
        print(f"{key} | {value['Nom']}")
    return


# Fonction pour updater le fichier 'menu.json' après avoir fait un request pour update la dispo d'un item.
def update_menu(item_id, disponibilite):
    global menu
    def update_file(menu):
        with open("menu.json", mode="w", encoding="UTF-8") as menu_file:
            # On dump le json dans le fichier avec les paramètres nécessaires.
            return json.dump(menu, menu_file, indent=6, ensure_ascii=False)
    # Ici, encore une fois, on doit vraiment définir une fonction récursive parce qu'on veut changer le menu directement.
    def parcourir_menu(menu, item_id, disponibilite):
        for key, value in menu.items():
            if 'items' in value:
                for item in value['items']:
                    if item['id'] == item_id:
                        # Si on trouve l'item avec l'id passé, on update la disponibilité avec la nouvelle disponibilité
                        # passé en paramètre.
                        item["disponible"] = False if disponibilite == '0' else True if disponibilite == '1' else item['disponible']
                        return
            else:
                parcourir_menu(value, item_id, disponibilite)
    parcourir_menu(menu, item_id, disponibilite)
    update_file(menu)
    # Après avoir update le file, on relit le fichier pour update notre menu dans le programme.
    menu=get_menu()
    
# Fonction pour afficher tous les comptes.
def show_all_users(matricule):
    if matricule != None:
        for i in range(len(all_users)):
            if all_users[i][0] == matricule:
                print(f"Matricule: {all_users[i][0]} | Nom: {all_users[i][1]} | Prénom: {all_users[i][2]}", end=" ")
                print(f"| Mot de passe: {all_users[i][3]} | Email: {all_users[i][4]} | Rôle: {all_users[i][5]} | ", end="")
                print(f"Actif: {'Oui' if all_users[i][6] == '1' else 'Non'}") 
        return               
    else:
        for i in range(len(all_users)):
            print(f"Matricule: {all_users[i][0]} | Nom: {all_users[i][1]} | Prénom: {all_users[i][2]}", end=" ")
            print(f"| Mot de passe: {all_users[i][3]} | Email: {all_users[i][4]} | Rôle: {all_users[i][5]} | ", end="")
            print(f"Actif: {'Oui' if all_users[i][6] == 1 else 'Non'}")
    return



def main():
    global menu
    menu = get_menu()
    users = get_users()
    get_item_dict(menu)
    # On vérifie si l'utilisateur a essayé de se connecter avec des paramètres passés.
    current_user = connect_by_parameters(users)
    # S'il n'a pas essayé, alors on va prompt le user à se connecter.
    if current_user == None:
        while True:
            current_user = get_user_data(users)
            # Si l'utilisateur est valide, on peut briser de la boucle infinie.
            if current_user != False:
                break
    role = current_user["Role"]
    # Boucle principale du programme qui handle les requests des users.
    while True:
        request_type, info, info_supplementaire = get_requete()
        analyze_request(request_type, info, info_supplementaire, role, menu, current_user['Matricule'])
    
def test():
    def test_valid_user():
        users = get_users()
        assert valid_user("20209230", "rnPass_25", users) == True
        assert valid_user("20209230", "", users) == False
        assert valid_user("", "", users) == False
        assert valid_user("20250710", "wrong_password", users) == False
        assert valid_user("20458102", "rlPass_30", users) == True

    def test_process_requete():
        assert process_requete("GET /api/menu/items/1") == ("GET", "/api/menu/items/1", None)
        assert process_requete("") == None
        assert process_requete("GET") == None
        assert process_requete("POST /api/commandes 3x1 4x2") == ("POST", "/api/commandes", ["3x1", "4x2"])
        assert process_requete("PUT /api/menu/items/3 disponible=0") == ("PUT", "/api/menu/items/3", ["disponible=0"])

    def test_show_item_info():
        get_item_dict(get_menu())
        show_item_info(menu, 1)
        show_item_info(menu, 2)
        show_item_info(menu, 60)
        show_item_info(menu, "")
        show_item_info(menu,[])


    test_valid_user()
    test_process_requete()
    test_show_item_info()

# test()
main()
