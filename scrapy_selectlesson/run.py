#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time : 2017/1/1 17:51
# @Author : woodenrobot
from scrapy import cmdline
import argparse
name = 'sel'

# create a project:
# scrapy startproject xxx(xxx is name of spider project)
# run a spider:scrapy crawl xxx [-a] (behind -a that we can input parameters,so that we will get them in the __init__() of spider)
# cmd = 'scrapy crawl {0}'.format(name)

cmd = 'scrapy crawl {0} -a info=SA17006127_hyyhdxwsls713_500_FL0530203_FL0630101_LB05203a01_PE0400503_CH4522101'.format(name)
cmdline.execute(cmd.split())