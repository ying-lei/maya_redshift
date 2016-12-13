import maya.cmds as cmds
import maya.mel as mel 
import os
 
def aovUI():
 
    if cmds.window('aovWindow', ex=1):
        cmds.deleteUI('aovWindow')
    
    cmds.loadPlugin('OpenEXRLoader.mll')
 
    cmds.window('aovWindow', w=150,h=100,s=0)
    cmds.formLayout('wndLayout')
 
    descAov = cmds.text( label="Redshift Load AOV's",w=150,h=22,fn='boldLabelFont',bgc=(0.15,0.15,0.15))
    aovsList = cmds.optionMenu( 'aovsListMenu',w=140,label='AOV',cc=loadAOV )
    activeAOVS = cmds.ls(et='RedshiftAOV')
    renderButton = cmds.button(w=150, label='RENDER', command=renderButtonPush)
    refreshButton = cmds.button(w=150, label='REFRESH UI', command=refreshButtonPush)
    aovsNames = [i.split('_', 1)[1] for i in activeAOVS]
 
    cmds.menuItem(label='Beauty')
 
    for item in aovsNames:
        cmds.menuItem(label=item )
 
    #Attach controls
    cmds.formLayout('wndLayout',e=1,af=[ (descAov,'top',0), (descAov,'left',0) ])
    cmds.formLayout('wndLayout',e=1,af=[ (aovsList,'top',25), (aovsList,'left',5) ])
    cmds.formLayout('wndLayout',e=1,af=[ (renderButton,'top',50) ])
    cmds.formLayout('wndLayout',e=1,af=[ (refreshButton,'top',75) ])
    
    
    cmds.showWindow('aovWindow')
 
def loadAOV(value):
    activeAOVS = cmds.ls(et='RedshiftAOV')
    aovsNames = [i.split('_', 1)[1] for i in activeAOVS]

    if activeAOVS == []:
        cmds.warning("No aov's setup")
        return

    rview = cmds.getPanel(sty = 'renderWindowPanel')
    selectedAOV = cmds.optionMenu('aovsListMenu',q=1,v=1)
    print "Selected AOV: %s" % selectedAOV
    
    img_temp_path = os.path.join(cmds.workspace(q=1, fullName=1), 'images/tmp')
    img_path = cmds.renderSettings(firstImageName=1)[0]
    framePadding= os.path.splitext(os.path.splitext(img_path)[0])[1]
    framePadding = len(str(framePadding))
    extention = os.path.splitext(img_path)[1]
    img_path = os.path.splitext(os.path.splitext(img_path)[0])[0]
    
    currentFrame = cmds.currentTime( query=True )
    currentFrame = '{:04d}'.format(int(currentFrame))
    if cmds.getAttr("defaultRenderGlobals.animation") == 1:
        currentFrame = "." + currentFrame
    else:
        currentFrame = ""
    
    if selectedAOV == "Beauty":
        full_path = os.path.join(img_temp_path, img_path)
        full_path += "{0}{1}".format(currentFrame, extention)
    
    else:
        selectedAOV = cmds.getAttr("rsAov_{0}.{1}".format(selectedAOV, 'name'))
        full_path = os.path.join(img_temp_path, img_path)
        full_path += ".{0}{1}{2}".format(selectedAOV, currentFrame, extention)
    
    full_path = full_path.replace('/','\\')
    print "Loaded: %s" % full_path
    cmds.renderWindowEditor(rview, e=True, li=full_path)

def refreshButtonPush(*args):
  aovUI()

def renderButtonPush(*args):
    # Save initial setup 
    mergeInitSetting = int(cmds.getAttr('redshiftOptions.exrForceMultilayer'))
    cropInitSetting = int(cmds.getAttr('redshiftOptions.autocrop'));
    
    # Ovveride
    cmds.setAttr('redshiftOptions.exrForceMultilayer',0)
    cmds.setAttr('redshiftOptions.autocrop',0)
    
    activeAOVS = cmds.ls(et='RedshiftAOV')
    for item in activeAOVS:
        mel.eval('setAttr -type "string" {0}.filePrefix "<BeautyPath>/<BeautyFile>.<RenderPass>"'.format(item))
 
    mel.eval("renderIntoNewWindow render")
    
    # Revert setup 
    cmds.setAttr('redshiftOptions.exrForceMultilayer',mergeInitSetting)
    cmds.setAttr('redshiftOptions.autocrop',cropInitSetting)

    for item in activeAOVS:
        mel.eval('setAttr -type "string" {0}.filePrefix "<BeautyPath>/<BeautyFile>"'.format(item))

    aovUI()
  
aovUI()
