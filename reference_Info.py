import maya.cmds as cc
import json

k_abcjsonP = r'D:\k_abc'

k_abcjson = k_abcjsonP.replace('\\','/')+'/k_referenceInfo.json'

def k_getreferenceInfo():

	k_referenceInfo={}


	#获取参考的 Resolved name
	kreflists = cc.file(q=True,reference=1)
	for kreflist in kreflists:
		#
		#获取勾选了的参考
		k_isloadre=cc.referenceQuery(kreflist,isLoaded=True )
		if k_isloadre:
			# 根据 resolved name 获取命名空间 命名空间不能包含特殊字符  ：号都不允许
			k_namespace=cc.referenceQuery(kreflist,namespace=1)
			#去除命名空间 前面的:号
			if k_namespace[0]==':':
				k_namespace= k_namespace[1:]


			#返回unresolvedName
			k_referencepath=cc.referenceQuery(kreflist,un=1,wcn=1,filename=1)
			#print k_referencepath

			#返回RN 名
			#krefNode = cc.file (kreflist,q=1,referenceNode=1)
			#print krefNode
			#返回关联的节点，dagPath
			k_refernodes = cc.referenceQuery(kreflist,nodes=True,dagPath=1)
			#返回关联节点中的 mesh节点  排除org节点
			k_refernode=cc.ls(k_refernodes,type='mesh',ni=1)

			#字典格式 {绝对名字：【文件路径，命名空间，关联的mesh节点（排除org），是否为二次参考（0不是，1是）】}
			k_referenceInfo[kreflist]=[k_referencepath,k_namespace,k_refernode,0]


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
	
	k_json = json.dumps( k_referenceInfo, indent=4,encoding='GBK')

	file = open(k_abcjson, 'w')
	file.write(k_json)
	file.close()



def makereference():

	error_reference=[]

	json_referenceInfo = json.loads(open(k_abcjson).read(),encoding='gbk')
	#print json_referenceInfo.keys()
	for referenceInfokey in json_referenceInfo:

		try:
			renrefer_path= json_referenceInfo[referenceInfokey][0].replace('_Rig','_Ren')
			renrefer_namespace =json_referenceInfo[referenceInfokey][1].replace('_Rig','_Ren')
			print renrefer_path
			print renrefer_namespace
			if ':' in renrefer_namespace:
				error_reference.append(json_referenceInfo[referenceInfokey][0])
			else:
				cc.file(renrefer_path,reference=1,namespace=renrefer_namespace)

		except:
			error_reference.append(json_referenceInfo[referenceInfokey][0])


		

		



if __name__=="__main__":
    k_getreferenceInfo()
    #makereference()