#coding:utf-8
#
import maya.cmds as cc
import json
import os
import maya.mel as mm

class k_ABC_procedure():
	def __init__(self):
		#返回当前文件路径
		self.k_sn=cc.file(q=1,sn=1)

		self.Geo    = ['*_geo','*:*_geo']
		self.Rig    = ['*_rig','*:*_rig']

		self.rig    = '_rig'
		self.ani    = '_ani'
		self.render = '_render'

		#定义mesh组
		self.geomesh=[]

		if self.k_sn:
			#提取abc节点名称
			self.k_abcnodename = os.path.splitext(os.path.basename(self.k_sn))[0]+'_AlembicNode'

			#设置json文件路径
			self.k_abcjsonP = os.path.dirname(self.k_sn)
			self.k_abcjson = os.path.dirname(self.k_sn).replace('\\','/')+'/'+self.k_abcnodename+'.json'

			self.k_abcname=''
			if self.k_sn[-3:]=='.mb' or self.k_sn[-3:]=='.ma':
				self.k_abcname=self.k_sn[:-3]+'.abc'
			if not self.k_abcname:
				cc.error('invaild scenes name!')
		else:cc.error('invaild scenes name!')


	def k_getabcInfo(self):
		#有重命名组可能会出问题 ，|PangLong_Rig1:Geometry会出问题  |PangLong_Rig:Geometry则不会
		#返回带 Geometry 命名的组 ，长名，是参考文件
		self.k_GeoT = cc.ls(self.Geo,type='transform',long=1,referencedNodes=1)
		#参考的大组名
		self.k_GeoTop = []
		#输出abc的root命令
		self.k_Geo_str = ""
		#abc的大组名
		self.k_abcTg = []

		if self.k_GeoT:
			#if k_GeoT and len(k_GeoT)== 1:
				#k_Geo_str = str(k_GeoT)
			#else:
			for i in self.k_GeoT:
				#k_Geo_str += ("-root "+"|" + str(i)+" ")
				#为输出ABC 编写字符
				try:

					ktgroup = cc.listRelatives(i,ap=1,f=1)
					if ktgroup and len(ktgroup)==1:
						ktgroupr = ktgroup[0].split('|')
						if len(ktgroupr)==2:
							#将参考的大组名字记录下来
							self.k_GeoTop.append(ktgroupr[1])

							#将abc的大组名记录下来
							abctg='|'+cc.ls(i)[0]

							self.k_abcTg.append(abctg)


							if ':' in i:
								#输出abc的时候的命令
								self.k_Geo_str += ("-root "+ str(i)+" ")
							else:
								self.k_Geo_str += ("-root "+ str(ktgroupr[1])+" ")
				except:
					cc.warning('Problems in the reference format!')


			#返回动画条的帧数范围
			self.startT=str(cc.playbackOptions( q=True,minTime=True) )
			self.endT=str(cc.playbackOptions( q=True,maxTime=True))


			self.k_jobArgs = "-frameRange " \
			+ self.startT \
			+ " " \
			+ self.endT \
			+ " -uvWrite -worldSpace " \
			+ self.k_Geo_str \
			+ " " \
			+ "-file" + " " + str(self.k_abcname) 

		else:
			print "This scenes havn't Geometry group"

		return self.k_jobArgs

	def k_expABC(self):

		self.k_jobArg=self.k_getabcInfo()

		cc.AbcExport(verbose=1,j=self.k_jobArg)

	def k_impABC(self,path):

		if cc.objExists('k_abcIM'):
			cc.delete('k_abcIM')
			cc.createNode('transform',n='k_abcIM')
		else:cc.createNode('transform',n='k_abcIM')


		if cc.ls(self.k_abcnodename,type='AlembicNode'):
			cc.error('Scenes already had abcNode!!!')
		else:
			cc.AbcImport(path,mode='import',reparent='k_abcIM')




	def k_getreferenceInfo(self):

		self.k_referenceInfo={}

		kgetinfo = self.k_getabcInfo()
		#获取参考的 Resolved name
		self.kreflists = cc.file(q=True,reference=1)
		for kreflist in self.kreflists:
			#
			#获取勾选了的参考
			k_isloadre=cc.referenceQuery(kreflist,isLoaded=True )
			#print kreflist
			if k_isloadre:
				# 根据 resolved name 获取命名空间 命名空间不能包含特殊字符  ：号都不允许
				k_namespace=cc.referenceQuery(kreflist,namespace=1)
				#去除命名空间 前面的:号
				if k_namespace[0]==':':
					k_namespace= k_namespace[1:]
				
				
				#返回unresolvedName
				k_referencepath=cc.referenceQuery(kreflist,un=1,wcn=1,filename=1)
				#print k_referencepath

				#返回RN名称
				k_referenceRN=cc.referenceQuery(kreflist,referenceNode=1)

				#返回RN 名
				#k_referenceRN = cc.file (kreflist,q=1,referenceNode=1)

				#返回关联的节点，dagPath
				k_refernodes = cc.referenceQuery(kreflist,nodes=True,dagPath=1)
				#返回关联节点中的 mesh节点  排除org节点
				k_refernode=cc.ls(k_refernodes,type='mesh',ni=1,long=1)
				#print k_refernode


				
				k_GeoTops=self.k_GeoTop

				#处理 有与没有设置命名空间的参考	
				if k_namespace:

					k_abcTg  =self.k_abcTg
					
					k_GeoTopgroup = [a for a in k_GeoTops if a.split(':')[0] == k_namespace]
					#print k_GeoTopgroup
					k_abcTopgroup = [a for a in k_abcTg   if a.split(':')[0] == '|'+k_namespace]
					#print k_abcTopgroup
					#字典格式 {绝对名字：【文件路径，命名空间，关联的mesh节点（排除org），是否为二次参考（0不是，1是）】}
					self.k_referenceInfo[kreflist]={'filepath':k_referencepath,'namespace':k_namespace,\
					'Topgroup':k_GeoTopgroup[0],'node':k_refernode,'abcgroup':k_abcTopgroup[0],\
					'RN':k_referenceRN,'subref':0}

				else:

					#没有命名空间的 大组等于abc大组
					k_GeoTopgroup = [a for a in k_GeoTops if a in k_refernodes]
					#print k_GeoTopgroup


					#字典格式 {绝对名字：【文件路径，命名空间，关联的mesh节点（排除org），是否为二次参考（0不是，1是）】}
					self.k_referenceInfo[kreflist]={'filepath':k_referencepath,'namespace':k_namespace,\
					'Topgroup':k_GeoTopgroup[0],'node':k_refernode,'abcgroup':k_GeoTopgroup[0],\
					'RN':k_referenceRN,'subref':0}


					'''
					#返回二次参考resolved name绝对名字
					k_child_referencelist=cc.referenceQuery(kreflist,ch=1,filename=1)
					if k_child_referencelist:
						#获取 二次参考 是勾选上的
						k_child_referencelist = [a for a in k_child_referencelist if cc.referenceQuery(a,isLoaded=True )]
						
						for k_child_referencelist in k_child_referencelist:
							#print k_child_referencelist
							#返回unresolvedName 文件路径
							k_child_referencepath=cc.referenceQuery(k_child_referencelist,un=1,wcn=1,filename=1)
							#print k_child_referencepath

							k_namespace=cc.referenceQuery(k_child_referencelist,namespace=1)
							#去除命名空间 前面的:号
							if k_namespace[0]==':':
								k_namespace= k_namespace[1:]


							k_referenceInfo[k_child_referencelist]=[k_child_referencepath,k_namespace,1]
					'''



		#return k_referenceInfo

		#找出ABC节点的名字
		k_GeoTops = self.k_GeoTop
		k_abcnodename = os.path.splitext(os.path.basename(self.k_abcname))[0]+'_AlembicNode'

		self.k_json = json.dumps(self.k_referenceInfo, indent=4,encoding='GBK')



		file = open(self.k_abcjson, 'w')
		file.write(self.k_json)
		file.close()

	def makereference(self):

		error_reference=[]

		self.json_referenceInfo = json.loads(open(self.k_abcjson).read(),encoding='gbk')
		#print json_referenceInfo.keys()
		for referenceInfokey in self.json_referenceInfo:

			try:
				#获取参考的路径和命名空间
				renrefer_path      = self.json_referenceInfo[referenceInfokey]['filepath'].replace(self.ani,self.render)
				renrefer_namespace = self.json_referenceInfo[referenceInfokey]['namespace'].replace(self.ani,self.render)
				renrefer_RN        = self.json_referenceInfo[referenceInfokey]['RN']
				#print renrefer_path
				#print renrefer_namespace
				#判断命名空间是否符合规定
				if ':' in renrefer_namespace:
					error_reference.append(self.json_referenceInfo[referenceInfokey])
				else:
					#cc.file(renrefer_path,reference=1,namespace=renrefer_namespace)
					cc.file(renrefer_path,loadReference=renrefer_RN)

			except:
				error_reference.append(self.json_referenceInfo[referenceInfokey])
		#print error_reference

	def k_connect_ABC(self):
		#获取abc节点名称
		abcnode = self.k_abcnodename 

		k_error=0

		if abcnode:
			#获取abc缓存节点 链接的shape节点
			abc_shapes=cc.listConnections(abcnode,s=0,sh=1,type='mesh')


			self.json_referenceInfo = json.loads(open(self.k_abcjson).read(),encoding='gbk')

			#以参考为单位 执行
			for referenceInfokey in self.json_referenceInfo:
				#获取大组名称
				k_Topgroup= self.json_referenceInfo[referenceInfokey]['Topgroup']
				#print k_Topgroup
				#获取参考关联mesh
				ref_node = self.json_referenceInfo[referenceInfokey]['node']
				#获取参考命名空间
				ref_namespace = self.json_referenceInfo[referenceInfokey]['namespace']
				#有命名空间的
				if ref_namespace:
					#json记录的参考 与 abc shape的对接
					for abc_shape in abc_shapes:
						#print abc_shape
						#去除abc_shape 头部的k_abcIM字符 再加进 原大组名称
						if '|'+k_Topgroup+abc_shape[7:] in ref_node:
							k_link = cc.listConnections(abc_shape,d=0,sh=1,c=1,p=1)
							#print k_link
							try:
								#cc.disconnectAttr(k_link[1],'|'+k_Topgroup+k_link[0],f=1)
								cc.connectAttr(k_link[1],'|'+k_Topgroup+k_link[0][7:],f=1)

							except:
								cc.warning('%s had something worry!!!' %abc_shape)
								k_error +=1
				#无命名空间的
				else:
					#json记录的参考 与 abc shape的对接
					for abc_shape in abc_shapes:
						print abc_shape
						#去除abc_shape 头部的k_abcIM字符 再加进 原大组名称
						if abc_shape[7:] in ref_node:
							print abc_shape[7:]
							k_link = cc.listConnections(abc_shape,d=0,sh=1,c=1,p=1)
							try:
								#cc.disconnectAttr(k_link[1],'|'+k_Topgroup+k_link[0],f=1)
								cc.connectAttr(k_link[1],k_link[0][7:],f=1)

							except:
								cc.warning('%s had something worry!!!' %abc_shape)
								k_error +=1	


			if k_error:
				cc.warning('had something worry!!!  abc file didnot delete')

			else:
				try:
					cc.delete('k_abcIM')
				except:
					cc.warning('delete abc group error')

	def findmesh(self,obj):
		try:
			#获取组里的元素
			objchs=cc.listRelatives(obj,f=1)

			for objch in objchs:
				#判断元素是否mesh

				if cc.ls(objch,type='mesh'):
					#是则添加进组
					self.geomesh.append(objch)

				#如果不是mesh则继续递归
				elif cc.ls(objch,type='transform'):
					self.findmesh(objch)
		except:
			pass

		return self.geomesh


	def k_save_render(self):
		k_sn=self.k_sn
		k_sbname = os.path.basename(k_sn)
		if k_sbname and self.rig in k_sbname.lower():
			k_ext = k_sbname.lower().find(self.rig)
			k_snreplace = k_sbname[k_ext:k_ext+4]
			k_snew = k_sn.replace(k_snreplace,self.render)



		k_opitem='"animationCurveOption","clipOption","poseOption",\
		"nurbsCrvOption","unusedNurbsSrfOption","deformerOption",\
		"unusedSkinInfsOption","groupIDnOption","locatorOption",\
		"ptConOption","pbOption","unitConversionOption","unknownNodesOption",\
		"setsOption","nurbsSrfOption","transformOption"'

		k_Geot = cc.ls(self.Geo,type='transform',long=1)
		k_Geotr = []
		k_Geotop=[]


		if k_Geot:
			for i in k_Geot:
				try:
					ktgroup = cc.listRelatives(i,ap=1,f=1)
					if ktgroup and len(ktgroup)==1:
						ktgroupr = ktgroup[0].split('|')
						if len(ktgroupr)==2:
							#将大组名字记录下来
							k_Geotop.append(ktgroupr[1])
							k_Geotr.append(i)


				except:
					cc.warning('Problems in the Group format!')

		#获取rig组
		k_Rig = cc.ls(self.Rig,type='transform',long=1)
		k_Rigs=[]
		if k_Rig:
			for i in k_Rig:
				#判断是否层级为2 的组 
				try:
					ktgroup2 = cc.listRelatives(i,ap=1,f=1)
					if ktgroup2 and len(ktgroup2)==1:
						ktgroupr2 = ktgroup2[0].split('|')
						if len(ktgroupr2)==2:
							k_Rigs.append(i)

				except:
					cc.warning('Problems in the Group format!')
	



		for Geotop in k_Geotop:
			k_tchild=cc.listRelatives(Geotop,c=1,f=1)
			k_delchild=[a for a in k_tchild if a in k_Rigs]
			#k_geochild=[a for a in k_tchild if a in k_Geotr]
			try:
				#kgeomeshs=self.findmesh(k_geochild[0])
				#去除 org 的mesh
				#kgeomesh=cc.ls(kgeomeshs,type='mesh',ni=1,l=1)
				cc.select(k_Geotr)
				cc.DeleteHistory()
				cc.select(cl=1)
				#print k_delchild
				cc.delete(k_delchild)
				mm.eval('source "cleanUpScene.mel"')
				mm.eval('scOpt_performOneCleanup ( {%s} );'% k_opitem) 

				cc.file(rename=k_snew)
				cc.file(f=1,op="v=0;",typ="mayaBinary",save=True)

			except:
				cc.warning('Something wrong in del unnecessary node!')


	def k_save_ani(self):
		k_opitem='"shaderOption"'

		k_sn=self.k_sn
		k_sbname = os.path.basename(k_sn)
		if k_sbname and self.rig in k_sbname.lower():
			k_ext = k_sbname.lower().find(self.rig)
			k_snreplace = k_sbname[k_ext:k_ext+4]
			k_snew = k_sn.replace(k_snreplace,self.ani)

		k_Geot = cc.ls(self.Geo,type='transform',long=1)
		k_Geotop=[]

		if k_Geot:
			for i in k_Geot:
				try:
					ktgroup = cc.listRelatives(i,ap=1,f=1)
					if ktgroup and len(ktgroup)==1:
						ktgroupr = ktgroup[0].split('|')
						if len(ktgroupr)==2:
							#将大组名字记录下来
							k_Geotop.append(ktgroupr[1])

				except:
					cc.warning('Problems in the Group format!')

		for Geotop in k_Geotop:
			k_tchild=cc.listRelatives(Geotop,c=1,f=1)

			k_delchild=[a for a in k_tchild if a in k_Geot]

			try:
				mm.eval('source "cleanUpScene.mel"')
				mm.eval('sets -e -forceElement initialShadingGroup %s;'% k_delchild[0])

				mm.eval('scOpt_performOneCleanup ( {%s} );'% k_opitem) 

				cc.file(rename=k_snew)
				cc.file(f=1,op="v=0;",typ="mayaBinary",save=True)

			except:
				cc.warning('Something wrong in del unnecessary node!')


	def k_export_abc(self):
		self.k_getreferenceInfo()
		self.k_expABC()


	def k_import_abc(self):
		self.makereference()
		self.k_impABC(self.k_abcname)
		self.k_connect_ABC()


	def tempwin(self):
		k_class=k_ABC_procedure()
		tempwindow = cc.window()
		templayout = cc.columnLayout(tempwindow,columnAttach=('both', 5), rowSpacing=10, columnWidth=250 )
		a=cc.button(label='保存ani版本',command="k_class=k_ABC_procedure()\nk_class.k_save_ani()")
		b=cc.button(label='保存render版本',command="k_class=k_ABC_procedure()\nk_class.k_save_render()")
		c=cc.button(label='导出abc缓存',command="k_class=k_ABC_procedure()\nk_class.k_export_abc()")
		d=cc.button(label='导入abc缓存',command="k_class=k_ABC_procedure()\nk_class.k_import_abc()")
		tempshow=cc.showWindow(tempwindow)
		






a=k_ABC_procedure()

a.tempwin()