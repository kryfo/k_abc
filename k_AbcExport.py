#coding:utf-8
import maya.cmds as cc

#b="-frameRange 1 10 -noNormals -ro -dataFormat ogawa -root |pSphere1 -file E:/work/8_0410_test/cache/alembic/asb.abc"
	
def k_getabcInfo():
	#返回带 :Geometry 命名的组
	k_GeoT = cc.ls('*:Geometry',type='transform')
	k_Geo_str = ""

	if k_GeoT:
		#if k_GeoT and len(k_GeoT)== 1:
			#k_Geo_str = str(k_GeoT)
		#else:
		for i in k_GeoT:
			#k_Geo_str += ("-root "+"|" + str(i)+" ")
			#为输出ABC 编写字符
			k_Geo_str += ("-root "+ str(i)+" ")

		#返回动画条的帧数范围
		startT=str(cc.playbackOptions( q=True,minTime=True) )
		endT=str(cc.playbackOptions( q=True,maxTime=True))
		#返回当前文件路径
		k_sn=cc.file(q=1,sn=1)
		k_abcname=''
		if k_sn[-3:]=='.mb' or k_sn[-3:]=='.ma':
			k_abcname=k_sn[:-3]+'.abc'

		k_attrPrefix='k_abc_'

		k_jobArgs = "-frameRange " \
		+ startT \
		+ " " \
		+ endT \
		+ " -uvWrite -worldSpace " \
		+ k_Geo_str \
		+ " " \
		+ "-file" + " " + str(k_abcname) 

	else:
		print "This scenes havn't Geometry group"

	return k_jobArgs

def k_expABC():

	k_jobArg=k_getInfo()

	cc.AbcExport(verbose=1,j=k_jobArg)

