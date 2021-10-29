#try: 
#	del idbChanged
#	del readHeader
#	del resolveProjectPath
#except: pass

from NatronGui import *
import NatronEngine
import datetime
import csv
import os
import shutil
import math
import glob

def readHeader (csv_file):
	# Read the csv file
	with file(csv_file,"r") as fr:
		#Read Headers
		reader = csv.reader(fr)
		header = next(reader, None)
		# Return header list
		return header

def cdbChanged( thisParam=False, thisNode=False, thisGroup=False, app=False, userEdited=False):
	if not NatronEngine.natron.isBackground():
		if thisParam.getScriptName() == 'load': # and userEdited :
			# Get Param for ID
			cid = str(thisNode.cid.getValue())
			cdbr = thisNode.cdb.getValue()
			combo_name = thisNode.cdb.getValue()

			# split out the Natron [Project] token and replace it with 
			project, filename = os.path.split(cdbr)
			project = app.projectPath.getValue()
			idb_path = os.path.join(project,"../ingredients-db/")
			csv_file = os.path.join(project, filename)

			# get csv headers
			header = readHeader(csv_file)

			# Debugging to the script editor
			print "Using CSV File: ", csv_file
			print "Using Headers: ", header
			print "Using Ingredient Path: ", idb_path
			print "ID: ", cid
			print "combo_name: ", combo_name
			#ingredientdbw = writeCSV(header, csv_file)

			with file(csv_file,"r")  as fr:
				csv_dict = csv.DictReader(fr)

				# setup counter and out vars
				text = "A1  CODE\t\tTYPE\t\t\tNAME\n"
				found = 0
				ri = 1
				oi = 0

				for row in csv_dict:
					# hacky row index counter
					ri=ri+1
					text = text + "A%s  %s\t\t%s\t\t%s\n" % (ri,  row['combo_id'] ,row['combo_category'],  row['combo_name'])

					if (row['combo_id'] == cid): 
						# build image file names

						if thisNode.load_images.get():
							# get coded wildcards, prob a much better way to do this outside of Natron
							elem0 = glob.glob("%s/%s*" % (idb_path, row['elem0']))
							elem1 = glob.glob("%s/%s*" % (idb_path, row['elem1']))
							elem2 = glob.glob("%s/%s*" % (idb_path, row['elem2']))
							elem3 = glob.glob("%s/%s*" % (idb_path, row['elem3']))
							elem4 = glob.glob("%s/%s*" % (idb_path, row['elem4']))


							# Convert back to [Project]
							p0, e0 = os.path.split(elem0[0])
							p1, e1 = os.path.split(elem1[0])
							p2, e2 = os.path.split(elem2[0])
							p3, e3 = os.path.split(elem3[0])
							p4, e4 = os.path.split(elem4[0])

							print p0, e0
							print p1, e1
							print p2, e2
							print p3, e3
							print p4, e4

							# set Parm values on Readers
							try:
								app.elem0.filename.setValue("[Project]/../ingredients-db/%s" % e0)
							except:
								app.elem0.filename.setValue("[Project]/../ingredients-db/0000-blank-transparent.png")

							try:
								app.elem1.filename.setValue("[Project]/../ingredients-db/%s" % e1)
							except:
								app.elem1.filename.setValue("[Project]/../ingredients-db/0000-blank-transparent.png")

							try:
								app.elem2.filename.setValue("[Project]/../ingredients-db/%s" % e2)
							except:
								app.elem2.filename.setValue("[Project]/../ingredients-db/0000-blank-transparent.png")

							try:
								app.elem3.filename.setValue("[Project]/../ingredients-db/%s" % e3)
							except:
								app.elem3.filename.setValue("[Project]/../ingredients-db/0000-blank-transparent.png")

							try:
								app.elem4.filename.setValue("[Project]/../ingredients-db/%s" % e4)
							except:
								app.elem4.filename.setValue("[Project]/../ingredients-db/0000-blank-transparent.png")


						# Set Natron Param Data
						# elem 0
						try: thisNode.combo_name.setValue(str(row['combo_name']))
						except: thisNode.combo_name.setValue()

						try: thisNode.combo_category.setValue(str(row['combo_category']))
						except: thisNode.combo_category.setValue("None")

						try: thisNode.cid.setValue(int(row['combo_id']))
						except: thisNode.cid.setValue(0)

						# Get elem Nodes
						try: app.elem0_transform.translate.setValue(float(row['elem0_translate_x']),0)
						except: app.elem0_transform.translate.setValue(0,0)
						try: app.elem0_transform.translate.setValue(float(row['elem0_translate_y']),1)
						except: app.elem0_transform.translate.setValue(.0,1)
						try: app.elem0_transform.rotate.setValue(float(row['elem0_rotate']))
						except: app.elem0_transform.rotate.setValue(0.0)
						try: app.elem0_transform.scale.setValue(float(row['elem0_scale_x']),0)											
						except: app.elem0_transform.scale.setValue(1.0,0)
						try: app.elem0_transform.scale.setValue(float(row['elem0_scale_y']),1)											
						except: app.elem0_transform.scale.setValue(1.0,1)
						try: app.elem0_transform.center.setValue(float(row['elem0_center_x']),0)										
						except: app.elem0_transform.center.setValue(512.0,0)
						try: app.elem0_transform.center.setValue(float(row['elem0_center_y']),1)										
						except: app.elem0_transform.center.setValue(512.0,1)

						# elem  1
						try: app.elem1_transform.translate.setValue(float(row['elem1_translate_x']),0)
						except: app.elem1_transform.translate.setValue(0.0,0)
						try: app.elem1_transform.translate.setValue(float(row['elem1_translate_y']),1)
						except: app.elem1_transform.translate.setValue(0.0,1)
						try: app.elem1_transform.rotate.setValue(float(row['elem1_rotate']))
						except: app.elem1_transform.rotate.setValue(0.0)
						try: app.elem1_transform.scale.setValue(float(row['elem1_scale_x']),0)						
						except: app.elem1_transform.scale.setValue(1.0,0)	
						try: app.elem1_transform.scale.setValue(float(row['elem1_scale_y']),1)						
						except: app.elem1_transform.scale.setValue(1.0,1)
						try: app.elem1_transform.center.setValue(float(row['elem1_center_x']),0)									
						except: app.elem1_transform.center.setValue(512.0,0)
						try: app.elem1_transform.center.setValue(float(row['elem1_center_y']),1)										
						except: app.elem1_transform.center.setValue(512.0,1)		

						# elem  2
						try: app.elem2_transform.translate.setValue(float(row['elem2_translate_x']),0)
						except: app.elem2_transform.translate.setValue(0.0,0)
						try: app.elem2_transform.translate.setValue(float(row['elem2_translate_y']),1)
						except: app.elem2_transform.translate.setValue(0.0,1)
						try: app.elem2_transform.rotate.setValue(float(row['elem2_rotate']))
						except: app.elem2_transform.rotate.setValue(0.0)
						try: app.elem2_transform.scale.setValue(float(row['elem2_scale_x']),0)											
						except: app.elem2_transform.scale.setValue(1.0,0)
						try: app.elem2_transform.scale.setValue(float(row['elem2_scale_y']),1)											
						except: app.elem2_transform.scale.setValue(1.0,1)
						try: app.elem2_transform.center.setValue(float(row['elem2_center_x']),0)										
						except: app.elem2_transform.center.setValue(512.0,0)
						try: app.elem2_transform.center.setValue(float(row['elem2_center_y']),1)										
						except: app.elem2_transform.center.setValue(512.0,1)		
						# elem  3
						try: app.elem3_transform.translate.setValue(float(row['elem3_translate_x']),0)
						except: app.elem3_transform.translate.setValue(0.0,0)
						try: app.elem3_transform.translate.setValue(float(row['elem3_translate_y']),1)
						except: app.elem3_transform.translate.setValue(0.0,1)
						try: app.elem3_transform.rotate.setValue(float(row['elem3_rotate']))
						except: app.elem3_transform.rotate.setValue(0.0)
						try: app.elem3_transform.scale.setValue(float(row['elem3_scale_x']),0)											
						except: app.elem3_transform.scale.setValue(1.0,0)
						try: app.elem3_transform.scale.setValue(float(row['elem3_scale_y']),1)											
						except: app.elem3_transform.scale.setValue(1.0,1)
						try: app.elem3_transform.center.setValue(float(row['elem3_center_x']),0)										
						except: app.elem3_transform.center.setValue(512.0,0)
						try: app.elem3_transform.center.setValue(float(row['elem3_center_y']),1)										
						except: app.elem3_transform.center.setValue(512.0,1)

						# elem  4
						try: app.elem4_transform.translate.setValue(float(row['elem4_translate_x']),0)
						except: app.elem4_transform.translate.setValue(0.0,0)
						try: app.elem4_transform.translate.setValue(float(row['elem4_translate_y']),1)
						except: app.elem4_transform.translate.setValue(0.0,1)
						try: app.elem4_transform.rotate.setValue(float(row['elem4_rotate']))
						except: app.elem4_transform.rotate.setValue(0.0)
						try: app.elem4_transform.scale.setValue(float(row['elem4_scale_x']),0)											
						except: app.elem4_transform.scale.setValue(1.0,0)
						try: app.elem4_transform.scale.setValue(float(row['elem4_scale_y']),1)											
						except: app.elem4_transform.scale.setValue(1.0,1)
						try: app.elem4_transform.center.setValue(float(row['elem4_center_x']),0)										
						except: app.elem4_transform.center.setValue(512.0,0)
						try: app.elem4_transform.center.setValue(float(row['elem4_center_y']),1)										
						except: app.elem4_transform.center.setValue(512.0,1)


			thisNode.cdb_rows.setValue(text)

		if thisParam.getScriptName() == 'save': # and userEdited :
			r = natron.questionDialog("Save File Warning","Saving will overwrite CSV file, are you sure?")
			if r.name == "eStandardButtonNo":
				return
			
			# Get Param for ID
			cid = str(thisNode.cid.getValue())
			cdbr = thisNode.cdb.getValue()
			combo_name = thisNode.cdb.getValue()

			# split out the Natron [Project] token and replace it with 
			project, filename = os.path.split(cdbr)
			project = app.projectPath.getValue()
			idb_path = os.path.join(project,"../ingredients-db/")
			csv_file = os.path.join(project, filename)
			csv_file_tmp = 	"%s.tmp" % csv_file

			# setup counter and out vars
			text = "A1  CODE\t\tTYPE\t\t\tNAME\n"
			ri = 1
			found = 0

			# get csv headers
			#header = readHeader(csv_file)			
			fr = file(csv_file,"r") 
			fw = file(csv_file_tmp,"w")

			reader = csv.reader(fr)
			header = next(reader, None)
			writer = csv.DictWriter(fw, fieldnames=header)
			writer.writeheader()

			# csv data
			fr = file(csv_file,"r") 
			with fr as y:
				rd = csv.DictReader(fr)
				
				for row in rd:
					if (row['combo_id'] == cid):
						writeParamRow(row, thisNode, app)
						found = 1
						writer.writerow(row)		
					else:
						writer.writerow(row)		

					ri = ri + 1
					text = text + "A%s  %s\t\t%s\t\t%s\n" % (ri,  row['combo_id'] ,row['combo_category'],  row['combo_name'])


					# print type(row)

				if not found:
					writeParamRow(row, thisNode, app)
					writer.writerow(row)		


			thisNode.cdb_rows.setValue(text)

			#path, file_full = os.path.split(idbr)
			#path = path+'/csv.old'
			#file_full = file_full+"_%s_%s.csv" % (id, str(datetime.datetime.today()).split()[0])
			#idbbak = os.path.join(path, file_full)
			#shutil.copy2( idbr, idbbak)
			os.rename( csv_file_tmp, csv_file)

			print "saved"
			savedate = datetime.datetime.today()
			sd = "Last Saved: %s" % savedate
			#thisNode.label_date.setValue(str(sd))
			#thisNode.refreshUserParamsGUI()


def writeParamRow(row, thisNode, app ):
	# get id and name params
	row['combo_id'] = thisNode.cid.getValue()
	row['combo_name'] = thisNode.combo_name.getValue()
	row['combo_category'] = thisNode.combo_category.getValue()

	# extract the ingredient code from filename and store in elem array
	p, code = os.path.split(app.elem0.filename.getValue())
	if code:
		row['elem0'] = code.split('-')[0]
	else:
		row['elem0'] = '0000'

	p, code = os.path.split(app.elem1.filename.getValue())
	if code:
		row['elem1'] = code.split('-')[0]
	else:
		row['elem1'] = '0000'

	p, code = os.path.split(app.elem2.filename.getValue())
	if code:
		row['elem2'] = code.split('-')[0]
	else:
		row['elem2'] = '0000'

	p, code = os.path.split(app.elem3.filename.getValue())
	if code:
		row['elem3'] = code.split('-')[0]
	else:
		row['elem3'] = '0000'

	p, code = os.path.split(app.elem4.filename.getValue())
	if code:
		row['elem4'] = code.split('-')[0]
	else:
		row['elem4'] = '0000'

	# elem 0
	row['elem0_translate_x'] = app.elem0_transform.translate.getValue(0)
	row['elem0_translate_y'] = app.elem0_transform.translate.getValue(1)
	row['elem0_rotate'] = round(app.elem0_transform.rotate.getValue(),2)
	row['elem0_scale_x'] = round(app.elem0_transform.scale.getValue(0),2)
	row['elem0_scale_y'] = round(app.elem0_transform.scale.getValue(1),2)
	row['elem0_center_x'] = app.elem0_transform.center.getValue(0)														
	row['elem0_center_y'] = app.elem0_transform.center.getValue(1)

	# elem  1
	row['elem1_translate_x'] = app.elem1_transform.translate.getValue(0)
	row['elem1_translate_y'] = app.elem1_transform.translate.getValue(1)
	row['elem1_rotate'] = round(app.elem1_transform.rotate.getValue(),2)
	row['elem1_scale_x'] = round(app.elem1_transform.scale.getValue(0),2)
	row['elem1_scale_y'] = round(app.elem1_transform.scale.getValue(1),2)
	row['elem1_center_x'] = app.elem1_transform.center.getValue(0)												
	row['elem1_center_y'] = app.elem1_transform.center.getValue(1)

	# elem  2
	row['elem2_translate_x'] = app.elem2_transform.translate.getValue(0)
	row['elem2_translate_y'] = app.elem2_transform.translate.getValue(1)
	row['elem2_rotate'] = round(app.elem2_transform.rotate.getValue(),2)
	row['elem2_scale_x'] = round(app.elem2_transform.scale.getValue(0),2)
	row['elem2_scale_y'] = round(app.elem2_transform.scale.getValue(1),2)
	row['elem2_center_x'] = app.elem2_transform.center.getValue(0)													
	row['elem2_center_y'] = app.elem2_transform.center.getValue(1)

	# elem  3
	row['elem3_translate_x'] = app.elem3_transform.translate.getValue(0)
	row['elem3_translate_y'] = app.elem3_transform.translate.getValue(1)
	row['elem3_rotate'] = round(app.elem3_transform.rotate.getValue(),2)
	row['elem3_scale_x'] = round(app.elem3_transform.scale.getValue(0),2)
	row['elem3_scale_y'] = round(app.elem3_transform.scale.getValue(1),2)
	row['elem3_center_x'] = app.elem3_transform.center.getValue(0)													
	row['elem3_center_y'] = app.elem3_transform.center.getValue(1)

	# elem  4
	row['elem4_translate_x'] = app.elem4_transform.translate.getValue(0)
	row['elem4_translate_y'] = app.elem4_transform.translate.getValue(1)
	row['elem4_rotate'] = round(app.elem4_transform.rotate.getValue(),2)
	row['elem4_scale_x'] = round(app.elem4_transform.scale.getValue(0),2)
	row['elem4_scale_y'] = round(app.elem4_transform.scale.getValue(1),2)
	row['elem4_center_x'] = app.elem4_transform.center.getValue(0)													
	row['elem4_center_y'] = app.elem4_transform.center.getValue(1)	


	print "writeParmRow", row

	return
