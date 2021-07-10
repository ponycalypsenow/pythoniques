import ctypes
import json 

SDL_INIT_EVERYTHING = 0xf231
SDL_WINDOWPOS_UNDEFINED = 0x1fff0000
SDL_HINT_RENDER_DRIVER = b"SDL_RENDER_DRIVER"
SDL_QUIT = 0x100
SDL_KEYDOWN = 0x300
SDL_KEYUP = 0x301
SDL_MOUSEMOTION = 0x400
SDL_MOUSEBUTTONDOWN = 0x401
SDL_MOUSEBUTTONUP = 0x402
SDL_BUTTON_LEFT = 1
SDL_BUTTON_RIGHT = 3
SDL_WINDOW_OPENGL = 0x00000002
SDL_WINDOW_SHOWN = 0x00000004
SDL_WINDOW_RESIZABLE = 0x00000020
SDL_RENDERER_ACCELERATED = 0x00000002
SDL_RENDERER_PRESENTVSYNC = 0x00000004
SDL_RENDERER_TARGETTEXTURE = 0x00000008
SDL_PIXELFORMAT_RGBA8888 = 0x16462004
SDL_TEXTUREACCESS_STREAMING = 1
SDL_TEXTUREACCESS_TARGET = 2
SDL_BLENDMODE_NONE = 0x00000000
SDL_BLENDMODE_BLEND = 0x00000001
SDL_FLIP_HORIZONTAL = 0x00000001
SDL_FLIP_VERTICAL = 0x00000002

PICO_PALETTE = [
    0x000000, 0x1D2B53, 0x7E2553, 0x008751, 0xAB5236, 0x5F574F, 0xC2C3C7, 0xFFF1E8, 0xFF004D, 0xFFA300, 0xFFEC27, 0x00E436, 0x29ADFF, 0x83769C, 0xFF77A8, 0xFFCCAA
]

PICO_FONT =[
    '0018666618623c060c300000000000003c183c3c067e3c7e3c3c00000e00703c3c187c3c787e7e3c663c1e666063663c7c3c7c3c7e66666366667e3c003c08002000000000000000000000000000000000000000000000000000000c183000',
    '001866663e66660c1818661800000003661866660e6066666666000018001866663c66666c60606666180c6c60777666666666661866666366660630600c1c001000600006000e006018066038000000000000001800000000000018181800',
    '001866ff600c3c18300c3c18000000066e3806061e7c600c66661818307e0c066e6666606660606066180c78607f7e6666666660186666633c660c30300c3600083c603c063c183e6000006018667c3c7c3e7c3e7e66666366667e18181800',
    '001800663c183800300cff7e007e000c76180c1c66067c183c3e00006000060c6e7e7c606678786e7e180c70606b7e667c667c3c1866666b183c1830180c630000067c603e663e667c38066c187f6666666666601866666b3c660c30180c39',
    '000000ff06306700300c3c1800000018661830067f06661866060000307e0c18606666606660606666180c7860636e66606678061866667f3c1830300c0c4100003e6660667e186666180678187f66666666603c1866667f1866181818184e',
    '000000667c666600181866181800183066186066066666186666181818001800626666666c60606666186c6c60636666603c6c6618663c7766186030060c0000006666606660183e6618066c186b66667c3e600618663c3e3c3e3018181800',
    '0018006618463f000c300000180018603c7e7e3c063c3c183c3c00180e0070183c667c3c787e603c663c38667e63663c600e663c183c186366187e3c033c0000003e7c3c3e3c1806663c06663c63663c6006607c0e3e1836660c7e0c183000',
    '000000000000000000000000300000000000000000000000000000300000000000000000000000000000000000000000000000000000000000000000000000ff000000000000007c00003c0000000000600600000000000000780000180000'
]

def flattenList(l):
    return [i for s in l for i in s]

def integerToRGB(rgb):
    return [(rgb >> 16) & 255, (rgb >> 8) & 255, rgb & 255]

def nibblesToInteger(high, low):
    return ((high << 4) | low) & 255

def integerToBytes(i):
    return [int(i, 2) for i in '{0:08b}'.format(i)]

class SDL_KeyboardEvent(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_uint32), ("timestamp", ctypes.c_uint32), ("windowID", ctypes.c_uint32), ("state", ctypes.c_uint8), ("repeat", ctypes.c_uint8),
        ("padding2", ctypes.c_uint8), ("padding3", ctypes.c_uint8), ("keysym", ctypes.c_uint32)
    ]

class SDL_MouseMotionEvent(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_uint32), ("timestamp", ctypes.c_uint32), ("windowID", ctypes.c_uint32), ("which", ctypes.c_uint32), ("state", ctypes.c_uint32),
        ("x", ctypes.c_int32), ("y", ctypes.c_int32), ("xrel", ctypes.c_int32), ("yrel", ctypes.c_int32)
    ]

class SDL_MouseButtonEvent(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_uint32), ("timestamp", ctypes.c_uint32), ("windowID", ctypes.c_uint32), ("which", ctypes.c_uint32), ("button", ctypes.c_uint8),
        ("state", ctypes.c_uint8), ("clicks", ctypes.c_uint8), ("padding1", ctypes.c_uint8), ("x", ctypes.c_int32), ("y", ctypes.c_int32)
    ]

class SDL_Event(ctypes.Union):
    _fields_ = [
        ("type", ctypes.c_uint32), ("key", SDL_KeyboardEvent), ("motion", SDL_MouseMotionEvent), ("button", SDL_MouseButtonEvent),("padding", ctypes.c_uint8 * 56)
    ]

class SDL_Rect(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_int), ("y", ctypes.c_int), ("w", ctypes.c_int), ("h", ctypes.c_int)
    ]

class SDL:
    sdl = None
    window = None
    renderer = None
    
    events = {
        "keyboard": {},
        "mouse": { "x": 0, "y": 0, "left": False, "right": False},
        "quit": False
    }

    def __init__(self):
        def bindFn(name, argtypes, restype):
            fn = getattr(self.sdl, name)
            fn.argtypes = argtypes
            fn.restype = restype
        
        self.sdl = ctypes.CDLL("sdl2.dll")
        bindFn("SDL_Init", [ctypes.c_int], ctypes.c_int)
        bindFn("SDL_Quit", [], None)
        bindFn("SDL_GetTicks", [], ctypes.c_uint32)
        bindFn("SDL_Delay", [ctypes.c_uint32], None)
        bindFn("SDL_CreateWindow", [ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint32], ctypes.c_void_p)
        bindFn("SDL_DestroyWindow", [ctypes.c_void_p], None)
        bindFn("SDL_PollEvent", [ctypes.c_void_p], ctypes.c_int)
        bindFn("SDL_CreateRenderer", [ctypes.c_void_p, ctypes.c_int, ctypes.c_uint32], ctypes.c_void_p)
        bindFn("SDL_DestroyRenderer", [ctypes.c_void_p], None)
        bindFn("SDL_SetHint", [ctypes.c_char_p, ctypes.c_char_p], ctypes.c_bool)
        bindFn("SDL_RenderSetScale", [ctypes.c_void_p, ctypes.c_float, ctypes.c_float],  ctypes.c_int)
        bindFn("SDL_CreateTexture", [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int, ctypes.c_int, ctypes.c_int], ctypes.c_void_p)
        bindFn("SDL_DestroyTexture", [ctypes.c_void_p], None)
        bindFn("SDL_SetTextureBlendMode", [ctypes.c_void_p, ctypes.c_int], ctypes.c_int)
        bindFn("SDL_SetRenderTarget", [ctypes.c_void_p, ctypes.c_void_p], ctypes.c_int)
        bindFn("SDL_RenderPresent", [ctypes.c_void_p], None)
        bindFn("SDL_RenderSetClipRect", [ctypes.c_void_p, ctypes.c_void_p], ctypes.c_int)
        bindFn("SDL_SetRenderDrawColor", [ctypes.c_void_p, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8], ctypes.c_int)
        bindFn("SDL_RenderClear", [ctypes.c_void_p], ctypes.c_int)
        bindFn("SDL_RenderDrawPoint", [ctypes.c_void_p, ctypes.c_int, ctypes.c_int], ctypes.c_int)
        bindFn("SDL_RenderDrawLine", [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int], ctypes.c_int)
        bindFn("SDL_RenderCopyEx", [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_double, ctypes.c_void_p, ctypes.c_int], ctypes.c_int)
        self.sdl.SDL_Init(SDL_INIT_EVERYTHING)
        self.sdl.SDL_SetHint(SDL_HINT_RENDER_DRIVER, b"opengl")
        self.window = self.sdl.SDL_CreateWindow(b"PyPicoSDL2", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, 512, 386, SDL_WINDOW_OPENGL | SDL_WINDOW_SHOWN | SDL_WINDOW_RESIZABLE)
        self.renderer = self.sdl.SDL_CreateRenderer(self.window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC)
        self.sdl.SDL_RenderSetScale(self.renderer, 2, 2)

    def _del_(self):
        self.sdl.SDL_DestroyRenderer(self.renderer)
        self.sdl.SDL_DestroyWindow(self.window)
        self.sdl.SDL_Quit()

    def getFrames(self):
        while not self.events["quit"]:
            frameStart = self.sdl.SDL_GetTicks()
            event = SDL_Event()
            while self.sdl.SDL_PollEvent(ctypes.byref(event)):
                if event.type == SDL_KEYDOWN or event.type == SDL_KEYUP:
                    if not event.key.repeat:
                        self.events["keyboard"][event.key.keysym] = event.type
                if event.type == SDL_MOUSEMOTION:
                    self.events["mouse"]["x"] = event.motion.x // 2
                    self.events["mouse"]["y"] = event.motion.y // 2
                elif event.type == SDL_MOUSEBUTTONDOWN:
                    if event.button.button == SDL_BUTTON_LEFT:
                        self.events["mouse"]["left"] = True
                    elif event.button.button == SDL_BUTTON_RIGHT:
                        self.events["mouse"]["right"] = True
                elif event.type == SDL_MOUSEBUTTONUP:
                    if event.button.button == SDL_BUTTON_LEFT:
                        self.events["mouse"]["left"] = False
                    elif event.button.button == SDL_BUTTON_RIGHT:
                        self.events["mouse"]["right"] = False
                elif event.type == SDL_QUIT:
                    self.events["quit"] = True
            yield self.events
            self.sdl.SDL_RenderPresent(self.renderer)
            frameTime = self.sdl.SDL_GetTicks() - frameStart
            if frameTime < 1000//60:
                self.sdl.SDL_Delay(1000//60 - frameTime)

    def stop(self):
        self.events["quit"] = True

    def setColor(self, r = 0, g = 0, b = 0, a = 255):
        self.sdl.SDL_SetRenderDrawColor(self.renderer, r, g, b, a)
            
    def clear(self):
        self.sdl.SDL_RenderClear(self.renderer)

    def clip(self, rx = 0, ry = 0, w = 512, h = 386):
        self.sdl.SDL_RenderSetClipRect(self.renderer, 0)
        self.sdl.SDL_RenderSetClipRect(self.renderer, ctypes.pointer(SDL_Rect(rx, ry, w, h)))

    def drawLine(self, rx0, ry0, rx1, rx2):
        self.sdl.SDL_RenderDrawLine(self.renderer, rx0, ry0, rx1, rx2)

    def createTexture(self, data, transparency = 0):
        texture = self.sdl.SDL_CreateTexture(self.renderer, SDL_PIXELFORMAT_RGBA8888, SDL_TEXTUREACCESS_TARGET, len(data[0]), len(data))
        self.sdl.SDL_SetTextureBlendMode(texture, SDL_BLENDMODE_BLEND)
        self.sdl.SDL_SetRenderTarget(self.renderer, texture)
        for y in range(len(data)):
            for x in range(len(data[y])):
                rgb = integerToRGB(PICO_PALETTE[data[y][x]])
                self.sdl.SDL_SetRenderDrawColor(self.renderer, rgb[0], rgb[1], rgb[2], 0 if data[y][x] == transparency else 255)
                self.sdl.SDL_RenderDrawPoint(self.renderer, x, y)
        self.sdl.SDL_SetRenderTarget(self.renderer, None)
        return texture

    def drawTexture(self, texture, tx, ty, w, h, rx, ry, flipHorizontal = False, flipVertical = False):
        flipFlag = (SDL_FLIP_HORIZONTAL if flipHorizontal else 0) | (SDL_FLIP_VERTICAL if flipVertical else 0)
        self.sdl.SDL_RenderCopyEx(self.renderer, texture, ctypes.pointer(SDL_Rect(tx, ty, w, h)), ctypes.pointer(SDL_Rect(rx, ry, w, h)), 0, 0, flipFlag)


class PICO:
    sdl = None
    gfx = None
    map = None

    def __init__(self, sdl, name):
        def parseSection(lines, parserFn):
            data = []
            for l in lines:
                if l.startswith("__"):
                    return [l, data]
                data.append(parserFn(l))
            return [None, data]

        def parseGfx(lines):
            [l, data] = parseSection(lines, lambda l: [int(c, 16) for c in l])
            self.gfx = self.sdl.createTexture(data)
            return l

        def parseMap(lines):
            [l, data] = parseSection(lines, lambda l: [nibblesToInteger(int(l[i], 16), int(l[i + 1], 16)) for i in range(0, len(l), 2)])
            self.map = data
            return l

        def parseFont(lines):
            def processLine(l):
                data = [integerToBytes(nibblesToInteger(int(l[i], 16), int(l[i + 1], 16))) for i in range(0, len(l), 2)]
                return [7 if c else 0 for c in flattenList(data)]
            
            [l, data] = parseSection(lines, processLine)
            self.font = self.sdl.createTexture(data)
            return l

        self.sdl = sdl
        parseFont(PICO_FONT)
        with open(name, "rt", encoding="utf-8") as f:
            lines = iter(f.read().split("\n"))
            l = next(lines, None)
            while l is not None:
                if l.startswith("__gfx__"):
                    l = parseGfx(lines)
                if l.startswith("__map__"):
                    l = parseMap(lines)
                else:
                    l = next(lines, None)

    def drawSprite(self, n, rx, ry, w = 1, h = 1, flipHorizontal = False, flipVertical = False):
        [tx, ty] = [8*(n%16), 8*(n//16)]
        self.sdl.drawTexture(self.gfx, tx, ty, int(8*w), int(8*h), rx, ry, flipHorizontal, flipVertical)

    def drawMap(self, mx, my, rx, ry, w = 128, h = 32):
        for y in range(my, min(my + h, len(self.map))):
            for x in range(mx, min(mx + w, len(self.map[0]))):
                self.drawSprite(self.map[y][x], rx + 8*(x - mx), ry + 8*(y - my))

    def printText(self, text, rx = 0, ry = 0):
        for (i, c) in enumerate(text):
            self.sdl.drawTexture(self.font, 8*(ord(c) - 32), 0, 8, 8, rx + 8*i, ry)

    def run(self):
        for frame in self.sdl.getFrames():
            self.sdl.clear()
            self.drawSprite(1, frame["mouse"]["x"], frame["mouse"]["y"])


pico = PICO(SDL(), "jelpi.p8")
pico.run()
