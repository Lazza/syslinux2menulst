#!/usr/bin/env python

"""Convert a syslinux/isolinux file to a GRUB menu.lst"""

import sys, re, argparse, os

__author__ = "Andrea Lazzarotto"
__copyright__ = "Copyright 2014+, Andrea Lazzarotto"
__license__ = "GPLv3+"
__version__ = "1.0"
__maintainer__ = "Andrea Lazzarotto"
__email__ = "andrea.lazzarotto@gmail.com"

parser = argparse.ArgumentParser(description='Convert a syslinux/isolinux file to a GRUB menu.lst.')
parser.add_argument('infile', metavar='FILE', help='Input file')
parser.add_argument('path', metavar='PATH', help='Absolute path in the disk structure, e.g. /menu.lst')
parser.add_argument('outdir', metavar='DIRECTORY', help='Output root directory (will be created if not present)')
args = parser.parse_args()

labelE = re.compile('(menu )?label\ (.*)', re.IGNORECASE)
kernelE = re.compile('(kernel|linux)\ (.*)', re.IGNORECASE)
kernel2E = re.compile('linux\.c32', re.IGNORECASE)
optionsE = re.compile('append\ (.*)', re.IGNORECASE)
initE = re.compile('initrd=([^\ ]*)', re.IGNORECASE)
init2E = re.compile('initrd\ (.*)', re.IGNORECASE)

def categorize(entry):
	e = '\n' + entry.lower()
	if '\ntimeout ' in e or '\nprompt' in e:
		return 'header'
	if '\nmenu exit' in e:
		return 'exit'
	if 'kbdmap.c32' in e:
		return 'keyboard'
	if '\nlabel' in e and ('\nkernel' in e or '\nlinux' in e or 'linux.' in e):
		return 'entry'
	if '\nmenu title' in e:
		return 'menu_begin'
	if '\nmenu end' in e:
		return 'menu_end'
	if '\nmenu separator' in e:
		return 'separator'
	return 'unknown'

def print_entry(entry, prefix):
	out = 'title ' + entry['label']
	if 'kernel' in entry:
		k = entry['kernel'].strip()
		if not k.startswith('/') and len(k) > 0:
			k = '/' + k
		out = out + '\nkernel ' + prefix + k
		if 'options' in entry:
			if len(k) > 0:
				out = out + ' ' + entry['options']
			else:
				if not entry['options'].startswith('/'):
					out = out + '/'
				out = out + entry['options']
	if 'initrd' in entry:
		out = out + '\ninitrd ' + prefix + entry['initrd'].strip()
	return out

def generate_entry(raw_entry):
	entry = {}
	for line in raw_entry.split('\n'):
		line = line.strip()
		label = labelE.match(line)
		if label:
			entry['label'] = label.group(2).replace('^', '').strip()
		kernel = kernelE.match(line)
		if kernel:
			entry['kernel'] = kernel.group(2).strip()
		kernel2 = kernel2E.search(line)
		if kernel2:
			entry['kernel'] = ''
		options = optionsE.match(line)
		if options:
			options = re.sub('initrd=([^\ ]*)', '', options.group(1))
			entry['options'] = options.strip()
		initrd = initE.search(line)
		if initrd:
			entry['initrd'] = initrd.group(1).strip()
		initrd2 = init2E.match(line)
		if initrd2:
			entry['initrd'] = initrd2.group(1).strip()

	return entry

def generate_lst(menu, name, previous, prefix):
	# this function returns a list of pairs (filename, menu)
	files = []
	out = ''
	for (c, e) in menu['entries']:
		if c == 'entry':
			entry = generate_entry(e)
			out = out + '\n\n' + print_entry(entry, prefix)
			continue
		if c == 'submenu':
			subname = name + '_' + str(e)
			out = (out + '\n\n' + 'title ' + menu['sub'][e]['title'] +
					'\n' + 'find --set-root ' + subname + '.lst\n' +
					'configfile ' + subname + '.lst')
			sub = generate_lst(menu['sub'][e], subname, name, prefix)
			files = files + sub
			continue
		if c == 'exit':
			title = sorted([l for l in e.split('\n') if 'label' in l.lower()],
					reverse = True)[0]
			if title.lower().startswith('menu'):
				title = ' '.join(title.split(' ')[2:])
			else:
				title = ' '.join(title.split(' ')[1:])
			out = (out + '\n\n' + 'title ' + title.replace('^', '') +
					'\n' + 'find --set-root ' + previous + '.lst\n' +
					'configfile ' + previous + '.lst')
			continue

	files.append((name + '.lst', out.strip()))
	return files

filename = args.infile
try:
	infile = open(filename, 'r')
except:
	print 'Error opening input file'
	exit(1)

if not args.path.startswith('/'):
	print 'Absolute path should start with "/"'
	exit(1)

if not args.outdir.endswith('/'):
	args.outdir = args.outdir + '/'

contents = '\n'.join([l.strip() for l in infile])
contents = re.sub('\nlabel', '\n\nlabel', contents)
blocks = contents.split('\n\n')
pairs = [(categorize(e), e) for e in blocks if e.strip() != '']
infile.close()

menu = {
	'title': 'main',
	'entries': [],
	'sub': []
}

# last element of this list is the current menu
m = [menu]

for (c, e) in pairs:
	if c == 'header' or c == 'keyboard':
		continue
	if c == 'menu_begin': # jump into the new menu
		newm = {
			'title': '',
			'entries': [],
			'sub': []
		}
		m[-1]['entries'].append(('submenu', len(m[-1]['sub'])))
		title = [l for l in e.split('\n') if 'menu title' in l.lower()][0]
		newm['title'] = ' '.join(title.split(' ')[2:])
		m[-1]['sub'].append(newm)
		m.append(newm)
		continue
	if c == 'menu_end': # go back to the previous menu
		m.pop(-1)
		continue
	if c == 'unknown':
		print 'WARNING: ignoring unknown entry'
		print '----\n' + e + '\n----'
		continue
	# default
	m[-1]['entries'].append((c,e))

if len(menu['sub']) == 1:
	menu = menu['sub'][0]

if args.path.endswith('.lst'):
	args.path = args.path[:-4]
if args.path.endswith('/'):
	args.path = args.path + 'menu'

prefix = os.path.dirname(args.path)
if prefix == '/':
	prefix = ''

menu_lst = generate_lst(menu, args.path, '', prefix)

directory = os.path.dirname(args.outdir + args.path)
if not os.path.exists(directory):
    os.makedirs(directory)

for (f, t) in menu_lst:
	outfile = open(args.outdir + f, 'w')
	outfile.write(t + '\n')
	outfile.close()
	print 'Saved file ' + args.outdir + f[1:]
