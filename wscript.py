#! /usr/bin/env python
# encoding: utf-8

top = '../'

def default(context):
	src = context.Node('jquery.ba-postmessage.js')
	
	# compiling global / jquery polluting version
	minified = src - '.js' + '.min.js'
	pre = src - '.js' + '_global_prefix.js'
	suf = src - '.js' + '_global_suffix.js'

	print("====== Compressing " + src.absolutepath + " into " + minified.absolutepath)
	minified.text = compress_with_closure_compiler(
		pre.text + src.text + suf.text
	)

	# compiling AMD version
	minified = src - '.js' + '_amd.min.js'
	pre = src - '.js' + '_amd_prefix.js'
	suf = src - '.js' + '_amd_suffix.js'

	print("========= Compressing " + src.path + " into " + minified.path)
	minified.text = compress_with_closure_compiler(
		pre.text + src.text + suf.text
	)

def compress_with_closure_compiler(code, compression_level = None):
	'''Sends text of JavaScript code to Google's Closure Compiler API
	Returns text of compressed code.
	'''
	# script (with some modifications) from 
	# https://developers.google.com/closure/compiler/docs/api-tutorial1

	import httplib, urllib, sys

	compression_levels = [
		'WHITESPACE_ONLY'
		, 'SIMPLE_OPTIMIZATIONS'
		, 'ADVANCED_OPTIMIZATIONS'
	]

	if compression_level not in compression_levels:
		compression_level = compression_levels[1] # simple optimizations

	# Define the parameters for the POST request and encode them in
	# a URL-safe format.
	params = urllib.urlencode([
	    ('js_code', code)
	    , ('compilation_level', compression_level)
	    , ('output_format', 'json')
	    , ('output_info', 'compiled_code')
	    , ('output_info', 'warnings')
	    , ('output_info', 'errors')
	    , ('output_info', 'statistics')
	    # , ('output_file_name', 'default.js')
	    # , ('js_externs', 'javascript with externs') # only used on Advanced. 
	  ])

	# Always use the following value for the Content-type header.
	headers = { "Content-type": "application/x-www-form-urlencoded" }
	conn = httplib.HTTPConnection('closure-compiler.appspot.com')
	conn.request('POST', '/compile', params, headers)
	response = conn.getresponse()

	if response.status != 200:
		raise Exception("Compilation server responded with non-OK status of " + str(response.status))

	compressedcode = response.read()
	conn.close()

	import json
	parts = json.loads(compressedcode)

	if 'errors' in parts:
		prettyerrors = ['\nCompilation Error:']
		for error in parts['errors']:
			prettyerrors.append(
				"\nln %s, ch %s, '%s' - %s" % (
					error['lineno']
					, error['charno']
					, error['line']
					, error['error']
				)
			)
		raise Exception(''.join(prettyerrors))

	return parts['compiledCode']

def test(context):
	
	a = context.Node('fileA.txt')
	c = context.Node('subfolder/')
	b = c + 'fileB.txt' # resulting in 'subfolder/fileB.txt' Node

	# the Nodes are not created immediately, but are
	# created on-demand
	assert(a.exists == False)
	assert(b.exists == False)

	# but you can hasten the process (it's like 'touch'):
	a.persist()
	b.persist()

	assert(a.exists == True)
	assert(b.exists == True)
	# ahhh, better. 

	# they are empty though. let's fill them with text.
	textforA = "This is some text for a"
	textforB = "This is some text for b"

	a.text = textforB 
	# oops, wrong place. let's copy by read from A + write to B
	b.text = a.text

	assert(a.exists == True)
	assert(b.exists == True)

	# you know, we approached that text copying in a wrong way
	# let's make file system copy the file. Will help when they are big.
	b.delete()

	# wait. Does the folder still exists?
	assert(c.exists == True)	
	# it can go too
	c.delete()	
	assert(c.exists == False)

	#and let's copy the right way
	a.copy(b)

	assert(b.exists == True)

	a.text = textforA

	print("file '%s'('%s') contains '%s'" % (a, a.absolutepath, a.text))
	print("file '%s'('%s') contains '%s'" % (b, b.absolutepath, b.text))

	a.delete()
	# deleting the folder deletes the contents.
	c.delete()

	assert(a.exists == False)
	assert(c.exists == False)

if __name__ == "__main__":
	print("This is a Wak (https://github.com/dvdotsenko/Wak) automation script file.\n(Export 'NOCLIMB' to shell scope and) run 'wak.py' against this folder.")