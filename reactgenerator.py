import random
import string
from subprocess import call
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from shutil import copyfile
import re
from PIL import Image

REACT_TEMPLATE = """import React from 'react';
import ReactDOM from 'react-dom';
import Button from '@material-ui/core/Button';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import BottomNavigation from '@material-ui/core/BottomNavigation';
import BottomNavigationAction from '@material-ui/core/BottomNavigationAction';
import FavoriteIcon from '@material-ui/icons/Favorite'
import Grid from '@material-ui/core/Grid';
import FormControlLabel from '@material-ui/core/FormControlLabel'
import Checkbox from '@material-ui/core/Checkbox'
import Radio from '@material-ui/core/Radio'
import Switch from '@material-ui/core/Switch'
import Typography from '@material-ui/core/Typography'

class App extends React.Component {
  render() {
    return (
        <React.Fragment>
          $PLACEHOLDER$
        </React.Fragment>
      );
  }
}

ReactDOM.render(<App />, document.getElementById('root'));"""

def RandomSentence():
    words = random.randrange(4, 10)
    yield (' '.join(RandomWord() for _ in range(words)) + '.').capitalize()

def RandomWord():
    chars = random.randrange(2, 10)
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(chars))

def RandomHtml():
    if random.randrange(2) == 0:
        yield RandomAppBar()
    yield RandomBody()
    if random.randrange(2) == 0:
        yield RandomBottomNavigation()

def RandomAppBar():
    yield '<AppBar position="static">'
    yield '<Toolbar>'
    yield RandomSentence()
    yield '</Toolbar>'
    yield '</AppBar>'
    
def RandomBottomNavigation():
    yield '<BottomNavigation>'
    actions = random.randrange(1, 4)
    for i in range(actions):
        yield '<BottomNavigationAction icon={<FavoriteIcon />} />'
    yield '</BottomNavigation>'
            
def RandomBody():
    yield '<Grid container spacing={16}>'
    if random.randrange(3) == 0:
        for _ in range(random.randrange(1, 6)):
            yield '<Grid item xs={4}>'
            yield RandomRow()
            yield '</Grid>'
            yield '<Grid item xs={7}>'
            yield RandomRow()
            yield '</Grid>'
    else:
        for _ in range(random.randrange(1, 6)):
            yield '<Grid item xs={12}>'
            yield RandomRow()
            yield '</Grid>'
    yield '</Grid>'
    
def RandomRow():
    for _ in range(random.randrange(1, 4)):
        itemtype = random.randrange(5)
        if itemtype == 0:
            yield '<Button variant="outlined">'
            yield RandomWord()
            yield '</Button>'
        elif itemtype == 1:
            yield '<FormControlLabel label="{}" control={{<Checkbox />}} />'.format(RandomWord())
        elif itemtype == 2:
            yield '<FormControlLabel label="{}" control={{<Radio />}} />'.format(RandomWord())
        elif itemtype == 3:
            yield '<FormControlLabel label="{}" control={{<Switch />}} />'.format(RandomWord())
        else:
            yield '<Typography>'
            yield RandomSentence()
            yield '</Typography>'

def generateDsl():
    result = ""
    def output(generator):
        nonlocal result
        if isinstance(generator, str):
            result += generator
        else:
            for g in generator:
                output(g)
        return result
    return output(RandomHtml())

def sanitizeDsl(dsl):
    dsl = re.sub(r' label="(.+?)"', 'label="dummy"', dsl)
    dsl = re.sub(r'</(.+?)>', '</>', dsl)
    return dsl

driver = webdriver.Firefox()
for i in range(10):
    dsl = generateDsl()
    with open('src/index.js', 'wt') as f:
        f.write(REACT_TEMPLATE.replace('$PLACEHOLDER$', dsl))
    with open('src/index_{i:02d}.dsl'.format(i=i), 'wt') as f:
        f.write(sanitizeDsl(dsl))
    call('npm run build', shell=True)
    driver.get('****')
    elem = driver.find_element_by_id('root')
    image_name = 'src/index_{i:02d}.png'.format(i=i)
    driver.save_screenshot(image_name)
    Image.open(image_name).crop((0, 0, 400, 800)).save(image_name)
driver.close()
