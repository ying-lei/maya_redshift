# ==================== Redshift Load AOV's ====================
# Create a custom UI to load AOV into Maya RenderView
# LIMITATION: Doesn't work on Token <Camera>
    

import maya.cmds as cmds
import maya.mel as mel 
import os

# Main UI 
def aovUI():
    getActiveAOVS() 
    
    if cmds.window('aovWindow', ex=1):
        cmds.deleteUI('aovWindow')
    
    cmds.window('aovWindow', w=150,h=100,s=0)
    cmds.formLayout('wndLayout')
 
    descAov = cmds.text( label="Redshift Load AOV's",w=150,h=22,fn='boldLabelFont',bgc=(0.15,0.15,0.15))
    aovsList = cmds.optionMenu( 'aovsListMenu',w=140,label='AOV',cc=loadAOV )
    renderButton = cmds.button(w=150, label='RENDER', command=renderButtonPush)
    refreshButton = cmds.button(w=150, label='REFRESH UI', command=refreshButtonPush)
 
    cmds.menuItem(label='Beauty')
 
    for item in aovNames:
        cmds.menuItem(label=item )
 
    #Attach controls
    cmds.formLayout('wndLayout',e=1,af=[ (descAov,'top',0), (descAov,'left',0) ])
    cmds.formLayout('wndLayout',e=1,af=[ (aovsList,'top',25), (aovsList,'left',5) ])
    cmds.formLayout('wndLayout',e=1,af=[ (renderButton,'top',50) ])
    cmds.formLayout('wndLayout',e=1,af=[ (refreshButton,'top',75) ])

    cmds.showWindow('aovWindow')
 
# Formatting AOV file path
def loadAOV(value):
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

# UI: RENDER button
def refreshButtonPush(*args):
  aovUI()

# UI: REFRESH button
def renderButtonPush(*args):

    getActiveAOVS()
    # Save initial setup 
    mergeInitSetting = int(cmds.getAttr('redshiftOptions.exrForceMultilayer'))
    cropInitSetting = int(cmds.getAttr('redshiftOptions.autocrop'))
    if activeAOVS == []:
        cmds.warning("No aov's setup")
        return
    aovNameInitSetting = cmds.getAttr('{0}.filePrefix'.format(activeAOVS[0]))
    
    # Ovveride
    cmds.setAttr('redshiftOptions.exrForceMultilayer',0)
    cmds.setAttr('redshiftOptions.autocrop',0)
    
    
    for item in activeAOVS:
        mel.eval('setAttr -type "string" {0}.filePrefix "<BeautyPath>/<BeautyFile>.<RenderPass>"'.format(item))
 
    mel.eval("renderIntoNewWindow render")
    
    # Revert setup 
    cmds.setAttr('redshiftOptions.exrForceMultilayer',mergeInitSetting)
    cmds.setAttr('redshiftOptions.autocrop',cropInitSetting)

    for item in activeAOVS:
        mel.eval('setAttr -type "string" {0}.filePrefix "{1}"'.format(item,aovNameInitSetting))

    aovUI()


# On startup
def checkRenderEnvSettings():
    if cmds.getAttr("defaultRenderGlobals.currentRenderer") != 'redshift':
        cmds.warning("Redshift is not current renderer")
        return
    cmds.loadPlugin('OpenEXRLoader.mll')
    aovUI()

# Update AOV list    
def getActiveAOVS():
    createdAOVS = cmds.ls(et='RedshiftAOV')
    
    activeAOVS = []
    aovNames = []

    global activeAOVS
    global aovNames
    
    del activeAOVS[:]
    del aovNames[:]

    for item in createdAOVS:
        if cmds.getAttr("{0}.enabled".format(item))!= 0:
            activeAOVS.append( item )
            aovNames.append( item.split('_', 1)[1])
   
    if activeAOVS == []:
        cmds.warning("No aov's setup")
        return

checkRenderEnvSettings()