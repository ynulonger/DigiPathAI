import os
import time
import sys
import numpy as np
import openslide
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable



from PIL import Image
sys.path.append('..')
from DigiPathAI.Segmentation import getSegmentation

digestpath_imgs = ['../examples/colon-cancer-1-slide.tiff',
					'../examples/colon-cancer-2-slide.tiff',
					'../examples/colon-cancer-3-slide.tiff',
					'../examples/colon-cancer-4-slide.tiff',
					'../examples/colon-cancer-5-slide.tiff']

paip_imgs       = ['']

camelyon_imgs   = ['']


models = ['dense', 'inception', 'deeplabv3', 'ensemble', 'epistemic']


for path in digestpath_imgs:
	ext = path[-4:]
	base_path = path[:-5]
	print (ext, base_path, base_path[:-5])
	quick = True
	tta_list = ['FLIP_LEFT_RIGHT', 'ROTATE_90', 'ROTATE_180', 'ROTATE_270']
	for model in models:

		print (model, quick, "======================================")
		if model == 'ensemble': 
			quick = False
		elif model == 'epistemic':
			quick = False
			tta_list = None

		getSegmentation(path, 
					patch_size  = 256, 
					stride_size = 128,
					batch_size  = 32,
					quick       = quick,
					tta_list    = tta_list,
					crf         = False,
					mask_path   = base_path + '-DigiPathAI_{}_mask.'.format(model) + ext,
					uncertainty_path   = base_path + '-DigiPathAI_{}_uncertainty.'.format(model)+ ext,
					status      = None,
					model       = model,
					mode        = 'colon')

		slide = openslide.OpenSlide(path)
		level = len(slide.level_dimensions) - 1
		img_dimensions = slide.level_dimensions[-1]
		img = np.array(slide.read_region((0,0), level, img_dimensions).convert('RGB'))

		mask = openslide.OpenSlide(base_path + '-DigiPathAI_{}_mask.'.format(model) + ext)
		level = len(mask.level_dimensions) - 1
		dimensions = mask.level_dimensions[-1]
		mask = np.array(mask.read_region((0,0), level, dimensions).convert('L'))

		uncertainty = openslide.OpenSlide(base_path + '-DigiPathAI_{}_uncertainty.'.format(model) + ext)
		level = len(uncertainty.level_dimensions) - 1
		dimensions = uncertainty.level_dimensions[-1]
		uncertainty = np.array(uncertainty.read_region((0,0), level, dimensions).convert('L'))

		mask = np.array(Image.fromarray(mask).resize(img_dimensions, Image.NEAREST))
		uncertainty = np.array(Image.fromarray(uncertainty).resize(img_dimensions))/255.0
		gt = np.array(Image.open(base_path[:-5] + 'gt.jpg').convert('RGB').resize(img_dimensions))

		fig, ax = plt.subplots(1, 4, figsize=(10, 40))
		im_ = ax[0].imshow(img)
		ax[0].set_xticklabels([])
		ax[0].set_yticklabels([])
		ax[0].set_xticks([])
		ax[0].set_yticks([])
		ax[0].set_aspect('equal')
		ax[0].tick_params(bottom='off', top='off', labelbottom='off', right='off', left='off', labelleft='off' )
		

		im_ = ax[1].imshow(img)
		gt_ = ax[1].imshow(gt, alpha = 0.5)
		ax[1].set_xticklabels([])
		ax[1].set_yticklabels([])
		ax[1].set_xticks([])
		ax[1].set_yticks([])
		ax[1].set_aspect('equal')
		ax[1].tick_params(bottom='off', top='off', labelbottom='off', right='off', left='off', labelleft='off' )
		
		im_ = ax[2].imshow(img)
		mask_ = ax[2].imshow(mask, alpha = 0.5, cmap='gray')
		ax[2].set_xticklabels([])
		ax[2].set_yticklabels([])
		ax[2].set_xticks([])
		ax[2].set_yticks([])
		ax[2].set_aspect('equal')
		ax[2].tick_params(bottom='off', top='off', labelbottom='off', right='off', left='off', labelleft='off' )
		
		im_ = ax[3].imshow(img)
		uncertain_ = ax[3].imshow(uncertainty, alpha = 0.5, cmap=plt.cm.RdBu_r)
		ax[3].set_xticklabels([])
		ax[3].set_yticklabels([])
		ax[3].set_xticks([])
		ax[3].set_yticks([])
		ax[3].set_aspect('equal')
		ax[3].tick_params(bottom='off', top='off', labelbottom='off', right='off', left='off', labelleft='off' )

		cax = fig.add_axes([ax[3].get_position().x1 + 0.01,
							ax[3].get_position().y0,
							0.01,
							ax[3].get_position().y1-ax[3].get_position().y0])
		fig.colorbar(uncertain_, cax=cax)

		plt.savefig(base_path+'DigiPath_Results_{}.png'.format(model), bbox_inches='tight')