import pygame

#Quelle: https://stackoverflow.com/questions/63435298/how-to-create-a-button-class-in-pygame

class Button:
    def __init__(self, color, x, y, width, height, text='', size=30):
        self.__color = color
        self.__x = x
        self.__y = y
        self.__width = width
        self.__height = height
        self.__text = text
        self.__size = size

    def draw(self, win,font, outline=None,):
        # Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.__x-2, self.__y-2, self.__width+4, self.__height+4), 0)
            
        pygame.draw.rect(win, self.__color, (self.__x, self.__y, self.__width, self.__height), 0)
        
        if self.__text != '':
            font = pygame.font.SysFont(font, self.__size) #Schriftart und -größe
            text = font.render(self.__text, 1, (0, 0, 0))
            win.blit(text, (self.__x + (self.__width/2 - text.get_width()/2), self.__y + (self.__height/2 - text.get_height()/2)))

    def isOver(self, pos):
        # Pos is the mouse position or a tuple of (x, y) coordinates
        if pos[0] > self.__x and pos[0] < self.__x + self.__width:
            if pos[1] > self.__y and pos[1] < self.__y + self.__height:
                return True
            
        return False
    
    def onClick(self, action=None):
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Check if mouse is over button and clicked
        if self.isOver(mouse_pos):
            if action is not None:
                action()
            return True
        return False
    
    

#Button implemented for testing

# Initialize pygame
pygame.init()

# Set up display
#win = pygame.display.set_mode((800, 600))
#pygame.display.set_caption("Button Example")

# Create a button
my_button = Button((0, 255, 0), 300, 250, 200, 100, "Click Me")

# Define an action function
def button_action():
    print("Button was clicked!")
    # You can put any code here that should run when the button is clicked

# Main game loop
running = True
if not running:
    #win.fill((255, 255, 255))  # Fill screen with white
    
    # Draw the button
    #my_button.draw(win, outline=(0, 0, 0))
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if button was clicked
            my_button.onClick(button_action)
    
    pygame.display.update()

pygame.quit()