import pygame
import math
import random

# ==============================================================================
#                               CONFIGURATION
# ==============================================================================
# Vous pouvez modifier les valeurs ci-dessous pour personnaliser la simulation.

# --- Paramètres de la Fenêtre ---
SCREEN_WIDTH = 1000  # Largeur de la fenêtre en pixels
SCREEN_HEIGHT = 800  # Hauteur de la fenêtre en pixels
FPS = 60             # Images par seconde (plus élevé = plus fluide, mais plus gourmand)

# --- Couleurs (utilisez des valeurs RGB : Rouge, Vert, Bleu de 0 à 255) ---
BACKGROUND_COLOR = (0, 0, 0)      # Couleur de fond (Noir)
BALL_COLOR = (255, 100, 255)      # Couleur de la balle (Rose vif)
RING_COLOR = (0, 200, 200)        # Couleur des cercles (Cyan)
TEXT_COLOR = (255, 255, 255)      # Couleur du texte (Blanc)
WIN_MESSAGE_COLOR = (0, 255, 0)   # Couleur du message de victoire (Vert)
LOSE_MESSAGE_COLOR = (255, 0, 0)  # Couleur du message de défaite (Rouge)

# --- Paramètres de la Balle ---
BALL_RADIUS = 10                  # Rayon de la balle en pixels
INITIAL_BALL_VX = 0               # Vitesse initiale horizontale de la balle (peut être 0)
INITIAL_BALL_VY = 0               # Vitesse initiale verticale de la balle (peut être 0)

# --- Paramètres Physiques ---
GRAVITY_STRENGTH = 0.05           # Force de la "gravité" radiale (vers le centre). Plus grand = plus d'attraction.
BOUNCE_COEFFICIENT = 0.85         # Coefficient de restitution (0.0 = pas de rebond, 1.0 = rebond parfait)

# --- Paramètres des Cercles (Anneaux) ---
NUM_CIRCLES = 25                  # Nombre total de cercles (entre 20 et 30 recommandé)
INITIAL_RING_RADIUS = 50          # Rayon du cercle le plus interne
RING_SPACING = 25                 # Espacement uniforme entre chaque cercle
RING_THICKNESS = 10               # Épaisseur des parois des cercles

# --- Paramètres des Ouvertures (Brèches) ---
GAP_ANGLE_DEGREES = 20            # Taille de l'ouverture dans chaque cercle en degrés (ex: 20 degrés)

# --- Paramètres de Rotation des Cercles ---
BASE_ROTATION_SPEED_DEG_PER_SEC = 5  # Vitesse de rotation du cercle le plus interne (en degrés par seconde)
SPEED_INCREMENT_DEG_PER_SEC = 0.2    # Augmentation de vitesse pour chaque cercle vers l'extérieur

# --- Paramètres de la Simulation ---
SIMULATION_DURATION_SECONDS = 50  # Durée totale de la simulation avant "Temps Écoulé"

# ==============================================================================
#                       FIN DE LA ZONE DE CONFIGURATION
# ==============================================================================


# --- Constantes internes (ne pas modifier) ---
# Conversion de l'angle de la brèche en radians pour les calculs Pygame
GAP_ANGLE_RADIANS = math.radians(GAP_ANGLE_DEGREES)

# --- Classes du jeu ---

class Ball:
    """Représente la balle qui se déplace et rebondit."""
    def __init__(self, x, y, radius, color, center_x, center_y, initial_vx, initial_vy):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vx = initial_vx  # Vitesse initiale en X
        self.vy = initial_vy  # Vitesse initiale en Y
        self.center_x = center_x
        self.center_y = center_y

    def update(self, dt):
        """Met à jour la position et la vitesse de la balle en appliquant la gravité."""
        # Calcul du vecteur de la balle vers le centre de l'écran
        dx = self.center_x - self.x
        dy = self.center_y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 1: # Évite la division par zéro si la balle est exactement au centre
            # Normalisation du vecteur pour obtenir la direction
            norm_dx = dx / distance
            norm_dy = dy / distance

            # Application de la gravité radiale
            self.vx += norm_dx * GRAVITY_STRENGTH * dt
            self.vy += norm_dy * GRAVITY_STRENGTH * dt

        # Mise à jour de la position
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, screen):
        """Dessine la balle sur l'écran."""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

class Ring:
    """Représente un anneau (cercle) avec une ouverture qui tourne."""
    def __init__(self, center_x, center_y, radius, thickness, color, gap_angle, rotation_speed_deg_per_sec):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.thickness = thickness
        self.color = color
        self.gap_angle = gap_angle # Taille de l'ouverture en radians
        self.rotation_speed = math.radians(rotation_speed_deg_per_sec) # Vitesse de rotation en radians par seconde
        self.current_gap_start_angle = 0 # Angle de départ de l'ouverture (initialement aligné)

    def update(self, dt):
        """Met à jour l'angle de rotation de l'anneau."""
        self.current_gap_start_angle += self.rotation_speed * dt
        # S'assurer que l'angle reste dans [0, 2*pi]
        self.current_gap_start_angle %= (2 * math.pi)

    def draw(self, screen):
        """Dessine l'anneau avec son ouverture."""
        # Définir le rectangle englobant pour le cercle
        rect = pygame.Rect(self.center_x - self.radius, self.center_y - self.radius,
                           self.radius * 2, self.radius * 2)

        # Calculer les angles pour les deux segments de l'anneau
        # Le premier segment va de (fin de la brèche) à 2*pi
        arc1_start = self.current_gap_start_angle + self.gap_angle
        arc1_end = self.current_gap_start_angle + 2 * math.pi

        # Le deuxième segment va de 0 à (début de la brèche)
        arc2_start = self.current_gap_start_angle
        arc2_end = self.current_gap_start_angle + self.gap_angle # This is the gap itself, so we draw up to it.

        # Pygame.draw.arc dessine dans le sens horaire.
        # Pour une brèche, on dessine le cercle en deux parties.
        # Partie 1: de l'angle de fin de la brèche à 2*pi (ou 0)
        # Partie 2: de 0 (ou 2*pi) à l'angle de début de la brèche

        # Dessiner le premier segment de l'anneau (après la brèche, jusqu'à la fin du cercle virtuel)
        pygame.draw.arc(screen, self.color, rect,
                        self.current_gap_start_angle + self.gap_angle,
                        self.current_gap_start_angle + 2 * math.pi,
                        self.thickness)

        # Dessiner le deuxième segment de l'anneau (du début du cercle virtuel jusqu'à la brèche)
        # On doit s'assurer que l'angle de début est inférieur à l'angle de fin pour draw.arc
        # Si la brèche traverse 0, cela devient un peu plus complexe.
        # La méthode la plus robuste est de dessiner un arc de (angle_fin_gap) à (angle_debut_gap + 2pi)
        # Mais Pygame.draw.arc n'est pas idéal pour ça.
        # On peut dessiner 2 arcs: un de (fin du gap) à (2*pi) et un autre de (0) à (début du gap)

        # Pour une meilleure gestion des angles qui traversent 0/2pi,
        # on peut dessiner un arc "principal" et un arc "secondaire" si la brèche est à cheval sur 0.
        # Cependant, la méthode actuelle avec deux arcs devrait fonctionner pour la plupart des cas
        # si l'angle de la brèche est petit.

        # Simplification: Dessiner un arc qui couvre la majeure partie du cercle,
        # et un deuxième arc pour la partie restante si la brèche est au milieu.
        # La méthode actuelle avec `self.current_gap_start_angle + 2 * math.pi`
        # et `0` est une approximation qui fonctionne si la brèche est "petite" et ne chevauche pas le point 0.

        # Une approche plus robuste pour la brèche:
        # On dessine un arc de `self.current_gap_start_angle + self.gap_angle` à `self.current_gap_start_angle + 2*math.pi`
        # et un autre arc de `self.current_gap_start_angle` à `self.current_gap_start_angle + self.gap_angle` (le gap)
        # Pour dessiner le reste, on peut faire:
        # from current_gap_start_angle + gap_angle to current_gap_start_angle + 2*pi
        # and from 0 to current_gap_start_angle
        # This is what's currently implemented, but the `0` can be problematic if current_gap_start_angle is small.

        # Corrected drawing for gap:
        # We draw the part of the circle *before* the gap, and the part *after* the gap.
        # The gap is from self.current_gap_start_angle to self.current_gap_start_angle + self.gap_angle
        
        # Draw the part from 0 to the start of the gap
        pygame.draw.arc(screen, self.color, rect,
                        0, # Start at 0 radians
                        self.current_gap_start_angle, # End at the start of the gap
                        self.thickness)
        
        # Draw the part from the end of the gap to 2*pi
        pygame.draw.arc(screen, self.color, rect,
                        self.current_gap_start_angle + self.gap_angle, # Start at the end of the gap
                        2 * math.pi, # End at 2*pi (full circle)
                        self.thickness)


    def check_collision(self, ball):
        """
        Vérifie la collision entre la balle et l'anneau, et gère le rebond.
        Retourne True si une collision a eu lieu, False sinon.
        """
        # Distance de la balle au centre de l'anneau
        dist_x = ball.x - self.center_x
        dist_y = ball.y - self.center_y
        distance_to_center = math.sqrt(dist_x**2 + dist_y**2)

        # Conditions pour être sur la paroi de l'anneau
        # La balle doit être à une distance du centre qui la place sur l'épaisseur de l'anneau
        min_ring_inner_edge = self.radius - self.thickness / 2
        max_ring_outer_edge = self.radius + self.thickness / 2

        # Vérifier si la balle est dans la zone de l'anneau (incluant le rayon de la balle)
        # Pour une collision, la distance du centre de la balle au centre de l'anneau
        # doit être entre (rayon_anneau - épaisseur/2 - rayon_balle) et (rayon_anneau + épaisseur/2 + rayon_balle)
        if not (min_ring_inner_edge - ball.radius < distance_to_center < max_ring_outer_edge + ball.radius):
            return False # Pas de collision avec l'épaisseur de l'anneau

        # Calculer l'angle de la balle par rapport au centre de l'anneau
        angle_ball = math.atan2(dist_y, dist_x)
        # Normaliser l'angle pour qu'il soit entre 0 et 2*pi
        if angle_ball < 0:
            angle_ball += 2 * math.pi

        # Vérifier si l'angle de la balle tombe dans l'ouverture
        gap_end_angle = (self.current_gap_start_angle + self.gap_angle) % (2 * math.pi)

        is_in_gap = False
        if self.current_gap_start_angle < gap_end_angle:
            # Cas normal où la brèche ne chevauche pas 0/2pi
            if self.current_gap_start_angle <= angle_ball <= gap_end_angle:
                is_in_gap = True
        else:
            # Cas où la brèche chevauche 0/2pi (ex: de 350 deg à 10 deg)
            if angle_ball >= self.current_gap_start_angle or angle_ball <= gap_end_angle:
                is_in_gap = True

        if is_in_gap:
            return False # La balle est dans l'ouverture, pas de collision avec le mur

        # Si la balle est sur la paroi et pas dans l'ouverture, il y a collision
        # Gérer le rebond "naturel"
        # Calculer le vecteur normal au point de collision (du centre de l'anneau vers la balle)
        normal_x = dist_x / distance_to_center
        normal_y = dist_y / distance_to_center

        # Calculer la composante de la vitesse le long de la normale (v . n)
        dot_product = ball.vx * normal_x + ball.vy * normal_y

        # Calculer la nouvelle vitesse après rebond
        # v_prime = v - (1 + e) * (v . n) * n
        ball.vx = ball.vx - (1 + BOUNCE_COEFFICIENT) * dot_product * normal_x
        ball.vy = ball.vy - (1 + BOUNCE_COEFFICIENT) * dot_product * normal_y

        # Repositionner légèrement la balle pour éviter qu'elle ne reste "enfoncée" dans le mur
        # Calculer la profondeur de pénétration
        # La distance idéale du centre de la balle au centre de l'anneau devrait être `self.radius`
        # On ajuste en fonction de si la balle est à l'intérieur ou à l'extérieur de l'anneau
        if distance_to_center < self.radius: # Balle est à l'intérieur de l'anneau
            overlap = (self.radius - ball.radius) - distance_to_center
            if overlap > 0:
                ball.x -= normal_x * overlap
                ball.y -= normal_y * overlap
        else: # Balle est à l'extérieur de l'anneau
            overlap = distance_to_center - (self.radius + ball.radius)
            if overlap < 0: # Si overlap est négatif, il y a pénétration
                ball.x -= normal_x * overlap
                ball.y -= normal_y * overlap

        return True

# --- Fonction principale du jeu ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simulation de Balle et Cercles Rotatifs")
    clock = pygame.time.Clock()

    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

    # Création de la balle
    ball = Ball(center_x, center_y, BALL_RADIUS, BALL_COLOR, center_x, center_y, INITIAL_BALL_VX, INITIAL_BALL_VY)

    # Création des anneaux
    rings = []
    for i in range(NUM_CIRCLES):
        radius = INITIAL_RING_RADIUS + i * RING_SPACING
        # La vitesse augmente légèrement pour chaque cercle vers l'extérieur
        rotation_speed = BASE_ROTATION_SPEED_DEG_PER_SEC + i * SPEED_INCREMENT_DEG_PER_SEC
        ring = Ring(center_x, center_y, radius, RING_THICKNESS, RING_COLOR, GAP_ANGLE_RADIANS, rotation_speed)
        rings.append(ring)

    # État du jeu
    running = True
    game_over = False
    win = False
    start_time = pygame.time.get_ticks() # Temps de début de la simulation
    simulation_duration_ms = SIMULATION_DURATION_SECONDS * 1000 # Durée de la simulation en millisecondes

    while running:
        dt = clock.tick(FPS) / 1000.0  # Temps écoulé depuis la dernière frame en secondes

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not game_over:
            # Mise à jour de la balle
            ball.update(dt)

            # Mise à jour et collision des anneaux
            for ring in rings:
                ring.update(dt)
                ring.check_collision(ball)

            # Vérifier la condition de victoire : la balle a franchi le cercle le plus externe
            outermost_ring_radius = rings[-1].radius if rings else 0 # Gérer le cas où il n'y a pas d'anneaux
            distance_from_center = math.sqrt((ball.x - center_x)**2 + (ball.y - center_y)**2)
            if distance_from_center > outermost_ring_radius + ball.radius + RING_SPACING / 2: # Ajout d'une petite marge
                win = True
                game_over = True

            # Vérifier le compte à rebours
            elapsed_time = pygame.time.get_ticks() - start_time
            if elapsed_time >= simulation_duration_ms:
                game_over = True
                win = False # Perdu si le temps est écoulé

        # --- Dessin ---
        screen.fill(BACKGROUND_COLOR) # Fond

        for ring in rings:
            ring.draw(screen)

        ball.draw(screen)

        # Affichage du temps restant
        remaining_time_ms = max(0, simulation_duration_ms - elapsed_time)
        remaining_time_s = remaining_time_ms // 1000
        font = pygame.font.Font(None, 50)
        text_surface = font.render(f"Temps: {remaining_time_s}s", True, TEXT_COLOR)
        screen.blit(text_surface, (10, 10))

        # Affichage des messages de fin de jeu
        if game_over:
            if win:
                message = "ÉVASION RÉUSSIE !"
                message_color = WIN_MESSAGE_COLOR
            else:
                message = "TEMPS ÉCOULÉ !"
                message_color = LOSE_MESSAGE_COLOR
            game_over_font = pygame.font.Font(None, 75)
            game_over_text = game_over_font.render(message, True, message_color)
            text_rect = game_over_text.get_rect(center=(center_x, center_y - 100))
            screen.blit(game_over_text, text_rect)

        pygame.display.flip() # Met à jour tout l'écran

    pygame.quit()

if __name__ == "__main__":
    main()