""" Redshift Load AOV's
Create a custom UI to load Redshift AOV into Maya RenderView
LIMITATION: Doesn't work on Token <Camera>
"""    

import maya.cmds as cmds
import maya.mel as mel 
import os

def checkRenderEnvSettings():
    """ Startup Checking: Returns Boolean
    1. Checks current renderer
    2. Checks unsupported tokens
    3. Checks image format
    4. Checks AOV enable
    5. Checks if active AOV exists
    Returns Boolean 
    """
    # 1
    if cmds.getAttr("defaultRenderGlobals.currentRenderer") != 'redshift':
        cmds.warning("Redshift is not current renderer")
        return False
    
    # 2
    imgPath = cmds.getAttr("defaultRenderGlobals.imageFilePrefix")
    if "<Camera>" in str(imgPath):
        cmds.warning("Token '<Camera>' is not supported")
        return False
    
    # 3
    if cmds.getAttr("redshiftOptions.imageFormat") != 1:
        cmds.warning("Only .exr format is supported")
        return False
        
    # 4
    if cmds.getAttr("redshiftOptions.aovGlobalEnableMode") != 1:
        cmds.warning("Please enable AOV render (not Batch Only)")
        return False
    
    # 5
    getActiveAOVS()
    if activeAOVS == []:
        cmds.warning("No aov's setup")
        return False
    
    cmds.loadPlugin('OpenEXRLoader.mll')
    aovUI()
    return True

# --------------------------------------------------------------------------------

def getActiveAOVS():
    """ Update AOV list """
    createdAOVS = cmds.ls(et='RedshiftAOV')

    global activeAOVS
    global aovNames
        
    activeAOVS = []
    aovNames = []
    
    del activeAOVS[:]
    del aovNames[:]

    for item in createdAOVS:
        if cmds.getAttr("{0}.enabled".format(item))!= 0:
            activeAOVS.append( item )
            aovNames.append( item.split('_', 1)[1])


def loadAOV(value):
    """ Formatting AOV file path """
    getActiveAOVS()

    rview = cmds.getPanel(sty = 'renderWindowPanel')
    selectedAOV = cmds.optionMenu('aovsListMenu',q=1,v=1)
    print "Selected AOV: %s" % selectedAOV
    
    imgTempPath = os.path.join(cmds.workspace(q=1, fullName=1), 'images/tmp')
    imgPath = cmds.renderSettings(firstImageName=1)[0]
    framePadding= os.path.splitext(os.path.splitext(imgPath)[0])[1]
    framePadding = len(str(framePadding))
    extension = os.path.splitext(imgPath)[1]
    imgPath = os.path.splitext(os.path.splitext(imgPath)[0])[0]
    
    currentFrame = cmds.currentTime( query=True )
    currentFrame = '{:04d}'.format(int(currentFrame))

    if cmds.getAttr("defaultRenderGlobals.animation") == 1:
        currentFrame = "." + currentFrame
    else:
        currentFrame = ""
    
    if selectedAOV == "Beauty":
        fullPath = os.path.join(imgTempPath, imgPath)
        fullPath += "{0}{1}".format(currentFrame, extension)
    
    else:
        selectedAOV = cmds.getAttr("rsAov_{0}.{1}".format(selectedAOV, 'name'))
        fullPath = os.path.join(imgTempPath, imgPath)
        fullPath += ".{0}{1}{2}".format(selectedAOV, currentFrame, extension)
    
    fullPath = fullPath.replace('/','\\')
    
    print "Loaded: %s" % fullPath
    cmds.renderWindowEditor(rview, e=True, li=fullPath)

# --------------------------------------------------------------------------------

def aovUI():
    """ Main UI """
    getActiveAOVS() 
    cmds.warning("AOV will be available after render (not IPR)")

    if cmds.window('aovWindow', ex=1):
        cmds.deleteUI('aovWindow')
    
    cmds.window('aovWindow', w=150,h=100,s=0)
    cmds.formLayout('wndLayout')
 
    descAov = cmds.text( label="Redshift Load AOV's",w=150,h=22,fn='boldLabelFont',bgc=(0.15,0.15,0.15))
    aovsList = cmds.optionMenu( 'aovsListMenu',w=140,label='AOV',cc=loadAOV )
    renderButton = cmds.button(w=150, label='RENDER', command=renderButtonPush)
    renderRegionButton = cmds.button(w=150, label='RENDER REGION', command=renderRegionButtonPush)
    refreshButton = cmds.button(w=150, label='REFRESH UI', command=refreshButtonPush)
 
    cmds.menuItem(label='Beauty')
 
    for item in aovNames:
        cmds.menuItem(label=item )
 
    #Attach controls
    cmds.formLayout('wndLayout',e=1,af=[ (descAov,'top',0), (descAov,'left',0) ])
    cmds.formLayout('wndLayout',e=1,af=[ (aovsList,'top',25), (aovsList,'left',5) ])
    cmds.formLayout('wndLayout',e=1,af=[ (renderButton,'top',50) ])
    cmds.formLayout('wndLayout',e=1,af=[ (renderRegionButton,'top',75) ])
    cmds.formLayout('wndLayout',e=1,af=[ (refreshButton,'top',100) ])

    cmds.showWindow('aovWindow')

# --------------------------------------------------------------------------------

def renderAOV(callback):
    # Check render settings
    if checkRenderEnvSettings() == False:
        return
    
    getActiveAOVS()
    # Save initial setup 
    mergeInitSetting = int(cmds.getAttr('redshiftOptions.exrForceMultilayer'))
    cropInitSetting = int(cmds.getAttr('redshiftOptions.autocrop'))
    aovNameInitSetting = cmds.getAttr('{0}.filePrefix'.format(activeAOVS[0]))
    
    # Ovveride
    cmds.setAttr('redshiftOptions.exrForceMultilayer',0)
    cmds.setAttr('redshiftOptions.autocrop',0)
       
    for item in activeAOVS:
        mel.eval('setAttr -type "string" {0}.filePrefix "<BeautyPath>/<BeautyFile>.<RenderPass>"'.format(item))
 
    callback()
    
    # Revert setup 
    cmds.setAttr('redshiftOptions.exrForceMultilayer',mergeInitSetting)
    cmds.setAttr('redshiftOptions.autocrop',cropInitSetting)

    for item in activeAOVS:
        mel.eval('setAttr -type "string" {0}.filePrefix "{1}"'.format(item,aovNameInitSetting))

    aovUI()


def performFullRender():
    mel.eval("renderIntoNewWindow render")


def performRegionRender():
    mel.eval("renderWindowRenderRegion renderView;")

# --------------------------------------------------------------------------------

def refreshButtonPush(*args):
    """ UI: REFRESH button """
    if checkRenderEnvSettings() == False:
        return
    aovUI()


def renderButtonPush(*args):
    """ UI: RENDER button """
    renderAOV(performFullRender)


def renderRegionButtonPush(*args):
    """ UI: RENDER REGION button """
    renderAOV(performRegionRender)


checkRenderEnvSettings()