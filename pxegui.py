#
# Quick ugly hack for a FAI installation GUI
# requires python-pygame
# adapted from Al Sweigart memory puzzle game...
#

import os, random, pygame, sys, math, subprocess
from pygame.locals import *

pygame.init()
videoinfo = pygame.display.Info()

FPS = 60 # frames per second, the general speed of the program
WINDOWWIDTH = videoinfo.current_w # size of window's width in pixels
WINDOWHEIGHT = videoinfo.current_h # size of windows' height in pixels
REVEALSPEED = 1 # speed boxes' sliding reveals and covers
BOARDWIDTH = 5 # number of columns of icons
BOARDHEIGHT = 2 # number of rows of icons
GAPSIZE = 2 # size of gap between boxes in pixels
XMARGIN = int(WINDOWWIDTH * 0.03)
YMARGIN = int(WINDOWHEIGHT * 0.6)
PROGRESSBARWIDTH = WINDOWWIDTH - (XMARGIN + XMARGIN)
NUMTASKS = 16
PCHUNK = int(PROGRESSBARWIDTH / NUMTASKS) 
 
BOXSIZE = ((WINDOWWIDTH - (XMARGIN + (GAPSIZE * (BOARDWIDTH+2)))) / BOARDWIDTH) # size of box height & width in pixels
BOXWIDTH = ((WINDOWWIDTH - (XMARGIN*2 + GAPSIZE*BOARDWIDTH) )  / BOARDWIDTH) # size of box height & width in pixels
BOXHEIGHT = ((WINDOWHEIGHT - (int(YMARGIN*1.1) + GAPSIZE)) / BOARDHEIGHT) # size of box height & width in pixels

assert (BOARDWIDTH * BOARDHEIGHT) % 2 == 0, 'Board needs to have an even number of boxes for pairs of matches.'

CONFDIR =      (0, 'confdir', "Initialiserar...")
SETUP =        (1,  'setup', "Setup..." )
DEFCLASS =     (2,  'defclass', "Definierar klasser...")
DEFVAR =       (3,  "defvar", "Definierar variabler...")
PARTITION =    (4,  "partition", "Partitonerar disk...")
MOUNTDISKS =   (5,  "mountdisks", "Monterar diskar...")
EXTRBASE =     (6,  "extrbase", "Packar upp grundsystemet...")
MIRROR  =      (7,  "mirror", "Monterar installationsspegeln...")
DEBCONF  =     (7,  "debconf", "Konfigurerar med Debconf")
PREPAREAPT =   (9, "prepareapt", "")
UPDATEBASE  =  (8, "updatebase", "Uppdaterar grundsystemet...")
INSTSOFT    =  (9, "instsoft", "Installerar programvara...")
CONFIGURE =    (10, "configure", "Konfigurerar systemet...")
FINISH =       (11, "finish", "Slutar...")
TESTS =        (12, "tests", "Testar...")
SAVELOG =      (13, "savelog", "Sparar loggfiler...")
FAIEND =       (14, "faiend", "Avslutar installationen...")
REBOOT =       (15, "reboot", "Startar om datorn...")

HWADDRESS = os.getenv('HWADDR')
HOSTNAME = os.getenv('HOSTNAME')


#               R    G    B
GRAY       = (100, 100, 100)
LIGHTGRAY  = (200, 200, 200)
WHITE      = (255, 255, 255)
TEAL       = (  0, 130, 153)
BLUE       = ( 38, 114, 236)
PURPLE     = (140,   0, 149)
DARKPURPLE = ( 81,  51, 171)
RED        = (172,  25,  61)
ORANGE     = (210,  71,  38)
GREEN      = (  0, 138,   0)
SKYBLUE    = (  9,  74, 178)   

GREY1      = (100, 100, 100)
GREY2      = (130, 130, 130)
GREY3      = (160, 160, 160)
GREY4      = (190, 190, 190)
GREY5      = (220, 220, 220)
GREY6      = (240, 240, 240)
GREY7      = (250, 250, 250) 

BGCOLOR = WHITE
LIGHTBGCOLOR = GRAY
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = LIGHTGRAY

WIN_CENTERX = int(WINDOWWIDTH / 2)
WIN_CENTERY = int(WINDOWHEIGHT / 2)

ALLTASKS = (CONFDIR, SETUP, DEFCLASS, DEFVAR, PARTITION, MOUNTDISKS, EXTRBASE, DEBCONF, UPDATEBASE, INSTSOFT, CONFIGURE, FINISH, TESTS, SAVELOG, FAIEND, REBOOT)
ALLCOLORS = (TEAL, RED, GREEN, BLUE, PURPLE, ORANGE, DARKPURPLE, SKYBLUE)

def main():
    global FPSCLOCK, DISPLAYSURF
    FPS = 60
    step = 0
    AMPLITUDE = 50
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((videoinfo.current_w, videoinfo.current_h), pygame.FULLSCREEN)

    pygame.mouse.set_visible(False)

    mousex = 0 # used to store x coordinate of mouse event
    mousey = 0 # used to store y coordinate of mouse event
    pygame.display.set_caption('Freedom Toaster')

    font = pygame.font.Font("Roboto-Thin.ttf", int(WINDOWHEIGHT * 0.08))

    text = font.render("Installerar SveLinux", True, (0, 128, 0))

    text = "Installerar SverigeLinux"

    DISPLAYSURF.fill(BGCOLOR)
    
    filecnt = 0
    infotext = "Konfigurerar installationssystem..."

    reboot = False


    while True: # main loop

        DISPLAYSURF.fill(BGCOLOR) # drawing the window    

        pygame.draw.rect(DISPLAYSURF, LIGHTGRAY, (XMARGIN,600,PROGRESSBARWIDTH,10), 0)

        fyle = open("/tmp/fai/fai-monitor.log")
        for lyne in fyle :
                lyne = lyne.rstrip('\n') 
                line = lyne.split(' ')
                for task in ALLTASKS:
                    if len(line) > 1:
                        if task[1] == line[1]:
		            infotext = task[2]
                            gridplace = task[0]           
                    for case in switch(line[0]):
                        if case('TASKBEGIN'):
                            if task[1] == line[1]:
                                drawProgressTasks(BLUE, gridplace)
                                if task[0] == 14:
                                    reboot = True
                            break
                        if case('TASKEND'):
                            if line[2] == '0':
                                if task[1] == line[1]:
                                    drawProgressTasks(GREEN, gridplace)
                                    if task[0] == 14:
                                        reboot = True
                            else:
                                if task[1] == line[1]:
                                    drawProgressTasks(ORANGE, gridplace)
                            break
                        if case('TASKSKIP'):
                            # print 10
                            break
                        if case('FAIREBOOT'):
                            # print 11
                            break
                        if case('HOOK'):
                            break
                        if case('check'):
                            # print "New install"
                            break
                        if case(): # default, could also just omit condition or 'if True'
                            break
                            # print line[0] + " Something Else!"
                            # No need to break here, it'll stop anyway
                    # displayWelcomeMessage(infotext)
        fyle.close()
        mouseClicked = False
       
        displayWelcomeMessage(infotext)
        displayHeader(text)
        displayHWaddr('MAC: ' + HWADDRESS)
        displayHostname(HOSTNAME)

        # displayWelcomeMessage()

        if reboot == True:
            # Display text "Installation finished. Press [Enter] to reboot"
            my_font = pygame.font.Font("Roboto-Regular.ttf", 16)
            my_string = "Installation klar. Tryck [ENTER] for att starta om"
            my_rect = pygame.Rect((50, 660, int(BOXWIDTH * 3), int(BOXHEIGHT)))
            rendered_text = render_textrect(my_string, my_font, my_rect, (0, 0, 0), BGCOLOR, 0)
            if rendered_text:
                DISPLAYSURF.blit(rendered_text, my_rect.topleft)

        # draw blue ball
        xPos =      math.cos(step) * AMPLITUDE
        yPos = 1 * math.sin(step) * AMPLITUDE
        #yPos = -1 * abs(math.sin(step) * AMPLITUDE) # uncomment this line to make the ball bounce
        pygame.draw.circle(DISPLAYSURF, GREY1, (int(xPos) + WIN_CENTERX, int(yPos) + WIN_CENTERY), 10)

        xPos =      math.cos(step-0.45) * AMPLITUDE
        yPos = 1 * math.sin(step-0.45) * AMPLITUDE
        #yPos = -1 * abs(math.sin(step) * AMPLITUDE) # uncomment this line to make the ball bounce
        pygame.draw.circle(DISPLAYSURF, GREY2, (int(xPos) + WIN_CENTERX, int(yPos) + WIN_CENTERY), 10)

        xPos =      math.cos(step-0.90) * AMPLITUDE
        yPos = 1 * math.sin(step-0.90) * AMPLITUDE
        #yPos = -1 * abs(math.sin(step) * AMPLITUDE) # uncomment this line to make the ball bounce
        pygame.draw.circle(DISPLAYSURF, GREY3, (int(xPos) + WIN_CENTERX, int(yPos) + WIN_CENTERY), 10)

        xPos =      math.cos(step-1.35) * AMPLITUDE
        yPos = 1 * math.sin(step-1.35) * AMPLITUDE
        #yPos = -1 * abs(math.sin(step) * AMPLITUDE) # uncomment this line to make the ball bounce
        pygame.draw.circle(DISPLAYSURF, GREY4, (int(xPos) + WIN_CENTERX, int(yPos) + WIN_CENTERY), 10)

        xPos =      math.cos(step-1.8) * AMPLITUDE
        yPos = 1 * math.sin(step-1.8) * AMPLITUDE
        #yPos = -1 * abs(math.sin(step) * AMPLITUDE) # uncomment this line to make the ball bounce
        pygame.draw.circle(DISPLAYSURF, GREY5, (int(xPos) + WIN_CENTERX, int(yPos) + WIN_CENTERY), 10)

        xPos =      math.cos(step-2.25) * AMPLITUDE
        yPos = 1 * math.sin(step-2.25) * AMPLITUDE
        #yPos = -1 * abs(math.sin(step) * AMPLITUDE) # uncomment this line to make the ball bounce
        pygame.draw.circle(DISPLAYSURF, GREY6, (int(xPos) + WIN_CENTERX, int(yPos) + WIN_CENTERY), 10)

        xPos =      math.cos(step-2.70) * AMPLITUDE
        yPos = 1 * math.sin(step-2.70) * AMPLITUDE
        #yPos = -1 * abs(math.sin(step) * AMPLITUDE) # uncomment this line to make the ball bounce
        pygame.draw.circle(DISPLAYSURF, GREY7, (int(xPos) + WIN_CENTERX, int(yPos) + WIN_CENTERY), 10)

        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True
            elif reboot == True and event.key == K_RETURN:
                restart()

        # Redraw the screen and wait a clock tick.
        pygame.display.update()
        FPSCLOCK.tick(FPS)

        step += 0.08
        step %= 2 * math.pi



def drawProgressTasks(color, task_no):
        
        pygame.draw.rect(DISPLAYSURF, color, (int(XMARGIN+(PCHUNK*task_no)),600,PCHUNK,10), 0)


def displayWelcomeMessage(infotext):
        my_font = pygame.font.Font("Roboto-Regular.ttf", 16)
        my_string = infotext
        my_rect = pygame.Rect((50, 640, int(BOXWIDTH * 3), int(BOXHEIGHT)))
        rendered_text = render_textrect(my_string, my_font, my_rect, (0, 0, 0), BGCOLOR, 0)
        if rendered_text:
            DISPLAYSURF.blit(rendered_text, my_rect.topleft)

def displayHeader(text):
    font = pygame.font.Font("Roboto-Thin.ttf", int(WINDOWHEIGHT * 0.08))
    header = font.render(text, True, (0, 128, 0))
    DISPLAYSURF.blit(header, (50, 180))    

def displayHWaddr(text):
    font = pygame.font.Font("Roboto-Thin.ttf", int(WINDOWHEIGHT * 0.04))
    header = font.render(text, True, (0, 128, 0))
    DISPLAYSURF.blit(header, (50, 240))

def displayHostname(text):
    font = pygame.font.Font("Roboto-Thin.ttf", int(WINDOWHEIGHT * 0.04))
    header = font.render(text, True, (0, 128, 0))
    DISPLAYSURF.blit(header, (50, 280))

class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False

class TextRectException:
    def __init__(self, message = None):
        self.message = message
    def __str__(self):
        return self.message

def render_textrect(string, font, rect, text_color, background_color, justification=0):
    """Returns a surface containing the passed text string, reformatted
    to fit within the given rect, word-wrapping as necessary. The text
    will be anti-aliased.

    Takes the following arguments:

    string - the text you wish to render. \n begins a new line.
    font - a Font object
    rect - a rectstyle giving the size of the surface requested.
    text_color - a three-byte tuple of the rgb value of the
                 text color. ex (0, 0, 0) = BLACK
    background_color - a three-byte tuple of the rgb value of the surface.
    justification - 0 (default) left-justified
                    1 horizontally centered
                    2 right-justified

    Returns the following values:

    Success - a surface object with the text rendered onto it.
    Failure - raises a TextRectException if the text won't fit onto the surface.
    """

    final_lines = []

    requested_lines = string.splitlines()

    # Create a series of lines that will fit on the provided
    # rectangle.

    for requested_line in requested_lines:
        if font.size(requested_line)[0] > rect.width:
            words = requested_line.split(' ')
            # if any of our words are too long to fit, return.
            for word in words:
                if font.size(word)[0] >= rect.width:
                    raise TextRectException, "The word " + word + " is too long to fit in the rect passed."
            # Start a new line
            accumulated_line = ""
            for word in words:
                test_line = accumulated_line + word + " "
                # Build the line while the words fit.    
                if font.size(test_line)[0] < rect.width:
                    accumulated_line = test_line 
                else: 
                    final_lines.append(accumulated_line) 
                    accumulated_line = word + " " 
            final_lines.append(accumulated_line)
        else: 
            final_lines.append(requested_line) 

    # Let's try to write the text out on the surface.

    surface = pygame.Surface(rect.size) 
    surface.fill(background_color) 

    accumulated_height = 0 
    for line in final_lines: 
        if accumulated_height + font.size(line)[1] >= rect.height:
            raise TextRectException, "Once word-wrapped, the text string was too tall to fit in the rect."
        if line != "":
            tempsurface = font.render(line, 1, text_color)
            if justification == 0:
                surface.blit(tempsurface, (0, accumulated_height))
            elif justification == 1:
                surface.blit(tempsurface, ((rect.width - tempsurface.get_width()) / 2, accumulated_height))
            elif justification == 2:
                surface.blit(tempsurface, (rect.width - tempsurface.get_width(), accumulated_height))
            else:
                raise TextRectException, "Invalid justification argument: " + str(justification)
        accumulated_height += font.size(line)[1]

    return surface

def restart():
    command = "/sbin/shutdown -r now"
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print output

if __name__ == '__main__':
    main()
