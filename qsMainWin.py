# -*- coding: utf-8 -*-
import os


from subprocess import Popen, PIPE
import re
import os
import sys
import maya.cmds as cmds
import maya.mel as mel
import qsMaya as qm
#import qsHouInMaya as QHM
#from bakeTextureSequence import *
#from qsVariables import *
from window import *
import melList



def __isLocalComputer():
    #return True
    handle = Popen('getmac /NH', shell=True, stdout=PIPE)
    hostid = handle.communicate()[0]
    handle.kill
    for addr in ('24-BE-05-E2-6C-9D', 'BC-AE-C5-77-79-D7', '00-50-56-C0-00-01' ):
        if hostid.find( addr ) != -1:
            return True
    else:
        return False

def __getPath( docStr, loc_computer ):
        if not docStr or (not docStr.startswith( 'del_path:' ) and not docStr.startswith( 'path:' ) ):
            return False
        if loc_computer:
            repStr = 'path:' if docStr.startswith( 'path:' ) else 'del_path:'
            finalPath = docStr.split('\n')[0].replace( repStr, '').strip()
        else:
            if docStr.startswith( 'del_path:' ):
                return False
            finalPath = docStr.split( '\n')[0].replace( 'path:', '').strip()
        return finalPath

HTTP_ROOT =   "http://localhost:8000" if __isLocalComputer() else  "http://vfx0300"


################################################################################


def w00_fun_scriptList(moduleList, *args, **kwargs ):
    if isinstance(moduleList, str) or isinstance( moduleList, unicode ):
        moduleList = [moduleList].sort()

    iconDirs = args[0]
    loc_computer = __isLocalComputer()
    #print 'loc-com:', loc_computer
    resultList = []
    for module in moduleList:
        #print 'import %s'%(module[0])
        module = list( module )
        if not module[1]:
            module[1] = module[0]
            
        execStr = 'import %s as %s'%(module[0], module[1] )            
        exec(execStr, globals()  )
        exec( 'reload(%s)'%(module[1]) )
        exec('modFunList = dir(%s)'%( module[1]) )
        modFunList = [fun for fun in modFunList if not fun.startswith('_') ]
        
        #uiList = eval( 'dir(%s)'%( "cmds_ui" ) )
        #print modFunList
        for fun in modFunList:
            funName = '%s.%s'%(module[1],fun)
            
            if not eval( 'callable(%s)'%funName):       #str( eval( 'type( %s.%s)'%(module[1],fun)  ) ) != "<type 'function'>":
                continue
            
            if str( eval( 'type( %s )'%(funName)  ) ) == "<type 'function'>":
                exec('docStr = %s.__doc__'%(funName ) )
            elif eval( 'hasattr(%s, "_menuStr")'%(funName) ):
                exec('docStr = %s._menuStr'%(funName ) )
                #print funName
            else:
                continue

            #exec('docStr = %s.%s.__doc__'%(module[1],fun) )
            if docStr:
                docStr = docStr.strip()

            if not docStr or not docStr.startswith( '{') or not docStr.endswith( '}' ):
                continue
            #print 'docStr', docStr
            #print fun
            try:
                docStr = eval( docStr )
            except:
                print 'got error on docStr evaluate!'
                print fun
                continue

            locMarker = False
            pathStr = docStr.get('path', None)
            if loc_computer and not pathStr:
                pathStr = docStr.get( 'del_path', None )
                locMarker=True
            if not pathStr:
                continue
            #print cmdPath

            #funName = module[1]+'.'+ eval( "%s.%s.__name__"%(module[1], fun) )
            #cmdPath = cmdPath + '/' + funName  + "()"

            cmdPath = '%s\n%s'%(pathStr, unicode(docStr.get( 'tip', None ))   )
            icon = docStr.get( 'icon', module[2])
            if not os.path.exists( icon ):
                for iconDir in iconDirs:
                    temp = icon.replace( '$ICONDIR', iconDir)
                    if os.path.exists( temp ):
                        icon = temp
                        break

            
            exeCmd = pathStr.rsplit( '/', 1)[-1].replace( 'ONLYSE', '')
            exeCmd =  '%s.%s'%(module[1], exeCmd)  if module[1] else exeCmd 
            if pathStr.endswith( 'ONLYSE' ):
                exeCmd = 'w00_fun_popCommand("%s")'%(exeCmd)
            
            #icon = icon.replace( '$ICONROOT', kwargs['iconRoot'] ) if icon else kwargs['defaultIcon']
            #print icon
            #helpDoc = docStr.get( 'help', None )
            #cmdUI = funName+'_ui' if funName+'_ui' in uiList else None

            resultList.append( (cmdPath, icon, exeCmd)   )
            resultList.sort()


    #existsCmdsUI =  dir( cmds_ui )
    return resultList


def getMelList(mels=melList.mels):
    melListInfo = {}
    melCmdList = []
    loc_computer = __isLocalComputer()
    for m in mels:
        #print m
        cmdPath = m.get( 'path', None)
        if not cmdPath and loc_computer:
            cmdPath = m.get('del_path', None)
        if not cmdPath:
            continue

        icon = m.get( 'icon', 'commandButton.png')
        cmdStr = cmdPath.rsplit( '/', 1)[-1].replace( 'ONLYSE', '')
        cmdStr = "mel.eval(\'%s\')"%(cmdStr)
        if cmdPath.strip().endswith( 'ONLYSE' ):
            cmdStr = '''w00_fun_popCommand(\"%s\")'''%(cmdStr)

        melCmdList.append( (cmdPath,icon,cmdStr) )
        melListInfo[ cmdStr ] = m
    return melCmdList, melListInfo 

melCmdList, melListData = getMelList()



def w00_fun_menuItemSet(name):
    if cmds.menuItem( name, q=True, checkBox=True):
        return True
    else:
        return False
    
def w00_fun_openProjectFolder():
    projDir = cmds.workspace(q =True, rootDirectory=True)
    if projDir.startswith('//'):
        projDir = projDir.replace('/', '\\')    
    os.startfile(  projDir )
    
       
def w00_fun_clearExecuter():
    tabNum = cmds.tabLayout( 'w00_02_tabLayout', q=True, sti=True )
    if tabNum == 1:
        cmds.cmdScrollFieldExecuter('w00_03_pythonWin', e=True, clear=True)
    elif tabNum == 2:
        cmds.cmdScrollFieldExecuter('w00_04_melWin', e=True, clear=True)


def w00_fun_executerAllButton():
    tabNum = cmds.tabLayout( 'w00_02_tabLayout', q=True, sti=True )
    if tabNum == 1:
        cmds.cmdScrollFieldExecuter('w00_03_pythonWin', e=True, executeAll=True)
        cmds.cmdScrollFieldExecuter('w00_03_pythonWin', e=True, clear=True)        
    elif tabNum == 2:
        cmds.cmdScrollFieldExecuter('w00_04_melWin', e=True, executeAll=True)
        cmds.cmdScrollFieldExecuter('w00_04_melWin', e=True, clear=True)


def w00_fun_executerSelButton():
    tabNum = cmds.tabLayout( 'w00_02_tabLayout', q=True, sti=True )
    if tabNum == 1:
        if cmds.cmdScrollFieldExecuter('w00_03_pythonWin', q=True,hsl=True):
            cmds.cmdScrollFieldExecuter('w00_03_pythonWin', e=True,execute=True)
    elif tabNum == 2:
        if cmds.cmdScrollFieldExecuter('w00_04_melWin', q=True,hsl=True):
            cmds.cmdScrollFieldExecuter('w00_04_melWin', e=True,execute=True)



def w00_fun_popCommand(funStr=None):
    itemStr = cmds.treeLister('w00_01', q=True, resultsPathUnderCursor=True)
    if itemStr == '':
        print 'popMenu error, Try again'
    else:
        funName = str( cmds.treeLister('w00_01', q=True, itemScript = itemStr )[1] )        
        if 'mel.eval' in funName:
            print funName
            #print 'usage:', melListData[funName]['usage']                        
            
            usageStr = melListData[funName]['usage'].strip()
            htmlUrl = melListData[funName].get( 'html', '')            
            if htmlUrl:
                if htmlUrl==True:
                    shortName = funName.rsplit('.',1)[-1]
                    htmlUrl = '%s/hq_maya/%s'%(HTTP_ROOT, shortName)
                    #if cmds.menuItem( 'w00_onlineHelpSwitch', q=True, checkBox=True ):                    
                    #    os.startfile( htmlUrl )
                htmlUrl = '\n//'+htmlUrl
                    
                        
            melCmd = re.match( r'\S*mel.eval\((.+)\)\S*', funName ).groups()[0]
            printStr = '\n//%s%s\n%s\n'%(melCmd, htmlUrl, usageStr)
            cmds.cmdScrollFieldExecuter('w00_04_melWin', e=True, appendText=printStr.decode('utf-8'))
            cmds.tabLayout( 'w00_02_tabLayout',e=True, sti=2)            
    
        else:
            funName = funName.strip()
            pattern = re.match( r'^w00_fun_popCommand\((.+)\)$', funName )
            if pattern:
                funName = pattern.groups()[0].rsplit('(')[0].strip()
                funName = funName[1:]
            else:                
                funName = funName.rsplit('(')[0].strip()
            
            
             
            #print funName
            #print funName
            #exec('docStr = eval(%s.__doc__)'%funName)
            if str( eval( 'type( %s )'%(funName)  ) ) == "<type 'function'>":
                exec('docStr = %s.__doc__'%(funName ) )
            elif eval( 'hasattr(%s, "_menuStr")'%(funName) ):
                exec('docStr = %s._menuStr'%(funName ) )           
            
            docStr = eval( docStr )
            
            usageStr = docStr.get('usage', '').strip().replace( '$fun', funName)
            htmlUrl = docStr.get( 'html', '')
            if htmlUrl:
                if htmlUrl==True:
                    shortName = funName.rsplit('.',1)[-1]
                    htmlUrl = '%s/hq_maya/%s'%(HTTP_ROOT, shortName)
                    #if cmds.menuItem( 'w00_onlineHelpSwitch', q=True, checkBox=True ):                    
                    #    os.startfile( htmlUrl )
                htmlUrl = '\n#'+htmlUrl
            helpStr = qm.HTMLToText( docStr.get( 'help', '')  ).getText().strip()
            helpStr = '"""\n' + helpStr + '\n"""' if helpStr else ''
            
            usageStr = '\n#%s%s\n%s\n%s'%(funName, htmlUrl, usageStr, helpStr)
            cmds.cmdScrollFieldExecuter('w00_03_pythonWin', e=True, appendText=usageStr.decode('utf-8') )
            cmds.tabLayout( 'w00_02_tabLayout',e=True, sti=1)




def w00_window_QSTools(*args, **kwargs):
    
    if cmds.window('w00', q=True, exists=True):
        #cmds.showWindow('w00')
        #return
        cmds.deleteUI( 'w00')
    
    iconDirs = []
    for iconDir in args[0]:
        if os.path.exists( iconDir ):
            iconDirs.append( iconDir )


    #---Collection nodeTreeLister Data    
    funList = w00_fun_scriptList([('qsMaya','qm', 'pythonFamily.png'),\
                          #('hou_in_maya','HIM', '%s\houdini\cloudsubmit\houdini_icon.png'%(houdiniPath) ),\
                          ('window','qmw', 'pythonFamily.png')], iconDirs
                        )

    
    #melCmdList, melListData = getMelList()
    
    funList.extend( melCmdList )
    
    #Sort and remove same functions
    temp, funs = [], []
    for i in funList[:]:
        if i[0] not in funs:
            funs.append( i[0] )
            fname = i[0].rsplit('/', 1)[-1]
            temp.append( (fname, i) )
    temp.sort()
    funList = [f[1] for f in temp]

    #globals()['funList'] = funList
    del temp, funs
    
    
    
    cmds.window('w00', title='HQ Maya',menuBar=True, retain=True, sizeable=True,rtf=True)
    
    
    #Script Editor menuBar    
    cmds.menu( 'w00_06_scrEditMenu', p='w00', label='Script Editor', tearOff=True )
    cmds.menuItem( 'w00_helpStringSwitch', p='w00_06_scrEditMenu', label='Help to script editor', checkBox=False )
    cmds.menuItem( 'w00_onlineHelpSwitch', p='w00_06_scrEditMenu', label='Open online help', checkBox=False )
    cmds.menuItem( p='w00_06_scrEditMenu',divider=True )
    cmds.menuItem( 'w00_07_comp', p='w00_06_scrEditMenu', label='Command Completion', checkBox=False,   command='cmds.cmdScrollFieldExecuter("w00_03_pythonWin", e=True,commandCompletion=w00_fun_menuItemSet("w00_07_comp"))\ncmds.cmdScrollFieldExecuter("w00_04_melWin", e=True,commandCompletion=w00_fun_menuItemSet("w00_07_comp"))')
    cmds.menuItem( 'w00_08_toolTip', p='w00_06_scrEditMenu', label='show Tooltip Help', checkBox=False, command='cmds.cmdScrollFieldExecuter("w00_03_pythonWin", e=True,showTooltipHelp=w00_fun_menuItemSet("w00_08_toolTip"))\ncmds.cmdScrollFieldExecuter("w00_04_melWin", e=True,showTooltipHelp=w00_fun_menuItemSet("w00_08_toolTip"))')
    cmds.menuItem( p='w00_06_scrEditMenu',divider=True )
    cmds.menuItem( 'w00_08_linNum', p='w00_06_scrEditMenu', label='Line numbers in errors', checkBox=False, command='cmds.cmdScrollFieldReporter("w00_05, e=True,lineNumbers=w00_fun_menuItemSet("w00_08_linNum"))' )
    cmds.menuItem( 'w00_09_echoAll', p='w00_06_scrEditMenu', label='Echo All Commands', checkBox=False, command='cmds.cmdScrollFieldReporter("w00_05", e=True,echoAllCommands=w00_fun_menuItemSet("w00_09_echoAll"))')
    cmds.menuItem( p='w00_06_scrEditMenu',divider=True )
    cmds.menuItem( 'w00_10_supCom', p='w00_06_scrEditMenu', label='Suppress Command Results', checkBox=False, command='cmds.cmdScrollFieldReporter("w00_05", e=True,suppressResults=w00_fun_menuItemSet("w00_10_supCom"))')
    cmds.menuItem( 'w00_11_supInfo', p='w00_06_scrEditMenu', label='Suppress Info Messages', checkBox=False, command='cmds.cmdScrollFieldReporter("w00_05", e=True,suppressInfo=w00_fun_menuItemSet("w00_11_supInfo"))')
    cmds.menuItem( 'w00_12_supWarn', p='w00_06_scrEditMenu', label='Suppress Warning Messages', checkBox=False, command='cmds.cmdScrollFieldReporter("w00_05", e=True,suppressWarnings=w00_fun_menuItemSet("w00_12_supWarn"))')
    cmds.menuItem( 'w00_13_supError', p='w00_06_scrEditMenu', label='Suppress Error Messages', checkBox=False, command='cmds.cmdScrollFieldReporter("w00_05", e=True,suppressErrors=w00_fun_menuItemSet("w00_13_supError"))')
    #meunu bar end
    
    
    
    #form Layout is main
    cmds.formLayout('w00_formLayout', p='w00',w=550, numberOfDivisions=100)
    
    #panelLayout UI
    cmds.paneLayout( 'w00_00_panelLayout', p='w00_formLayout', configuration='right3' )
    cmds.nodeTreeLister('w00_01', p='w00_00_panelLayout', addItem=[(path,icon,cmd) for path,icon,cmd in funList]  )
    
    #pop menu for treeLister
    cmds.popupMenu('w00_15_popMenu', p='w00_01')
    cmds.menuItem(p='w00_15_popMenu',label='CommandToScriptEditor', command='w00_fun_popCommand()')
    #cmds.menuItem(p='w00_15_popMenu',label='Online help/To Script editor', command='w00_online_help()' )
    
    
    
    #script ediotrs tabLayout UI
    cmds.tabLayout('w00_02_tabLayout',p='w00_00_panelLayout', innerMarginWidth=5, innerMarginHeight=5)
    cmds.cmdScrollFieldExecuter('w00_03_pythonWin', p='w00_02_tabLayout', cco=False, sth=False, sourceType="python",sln=True)
    cmds.cmdScrollFieldExecuter( 'w00_04_melWin',p='w00_02_tabLayout', cco=False, sth=False, sourceType="mel", sln=True)
    
    #cmds.formLayout('w00_02_neFormLayout', p='w00_02_tabLayout')
    #if cmds.scriptedPanel('w00_02_nodeEditor', q=True, exists=True): 
        #cmds.deleteUI('w00_02_nodeEditor')
    #cmds.scriptedPanel('w00_02_nodeEditor', p='w00_02_neFormLayout', type="nodeEditorPanel", label="Node Editor")
    #cmds.formLayout('w00_02_neFormLayout', e=True, p='w00_02_tabLayout', af=[('w00_02_nodeEditor',s,0) for s in ("top","bottom","left","right")])
    #cmds.cmdScrollFieldExecuter( 'w00_04_houWin',p='w00_02_tabLayout', cco=False, sth=False, sourceType="python", sln=True)
    
    
    cmds.tabLayout( 'w00_02_tabLayout', e=True, tabLabel=(('w00_03_pythonWin', 'Python'), ('w00_04_melWin', 'MEL'))  )  #, ('w00_02_neFormLayout', 'Node Editor'))     )    
    cmds.cmdScrollFieldReporter('w00_05', p='w00_00_panelLayout', ln=True, eac=False, sr=False, si=False, sw=False, se=False, clr=True)
    
    
    #buttons UI
    cmds.rowLayout('w00_14_rowLayout', p='w00_formLayout',numberOfColumns=6)
    cmds.iconTextButton(label='ProjectFolder',p='w00_14_rowLayout', width=50, style='iconOnly', image='fileOpen.png', command='w00_fun_openProjectFolder()')
    #cmds.button(label='ProjectFolder',p='w00_14_rowLayout', bgc=[1,.6,0], command='w00_fun_openProjectFolder()')
    cmds.iconTextButton(label='ClearInput', p='w00_14_rowLayout', width=50, style='iconOnly', image='clearHistory.png', command='w00_fun_clearExecuter()')
    cmds.iconTextButton(label='ExecuteAll', p='w00_14_rowLayout', width=50, style='iconOnly', image='executeAll.png', command='w00_fun_executerAllButton()')
    cmds.iconTextButton(label='Execute', p='w00_14_rowLayout', width=50, style='iconOnly', image='execute.png', command='w00_fun_executerSelButton()')
    #cmds.button(label='Execute', p='w00_14_rowLayout', command='w00_fun_executerSelButton()')
    cmds.iconTextButton(label='ClearDown', p='w00_14_rowLayout', width=50, style='iconOnly', image='clearInput.png', command='cmds.cmdScrollFieldReporter("w00_05",e=True,clr=True)')
    #cmds.button(label='ClearDown', p='w00_14_rowLayout', command='cmds.cmdScrollFieldReporter("w00_05",e=True,clr=True)')
    
    
    
    cmds.formLayout('w00_formLayout', e=True,\
                    af=[('w00_00_panelLayout', 'top', 0), ('w00_00_panelLayout', 'left', 0), ('w00_00_panelLayout', 'bottom', 0),('w00_00_panelLayout', 'right', 0), ('w00_14_rowLayout', 'top', 0), ('w00_14_rowLayout', 'right', 0) ],\
                    attachNone=[('w00_14_rowLayout', 'left'), ('w00_14_rowLayout', 'bottom')]
                        )
    
    cmds.showWindow('w00')