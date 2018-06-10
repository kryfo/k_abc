#coding:utf-8
import maya.cmds as cc

#path=abc文件路径
def k_impABC(path):

	k_jobArg=k_getInfo()

	cc.AbcImport(path,mode='import')


