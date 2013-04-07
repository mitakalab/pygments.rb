# -*- coding: utf-8 -*-
"""
pygments.formatters.mitakalab
~~~~~~~~~~~~~~~~~~~~~~~~~~

MitakaLab specific formatter for HTML output.
Based on the standard HTML formatter.

:copyright: Copyright 2012 by the MitakaLab team (http://mitakalab.com).
:license: BSD, see LICENSE for details.
"""

import os
import sys
import StringIO

from pygments.formatter import Formatter
from pygments.token import Token, Text, STANDARD_TYPES
from pygments.util import get_bool_opt, get_int_opt, get_list_opt # hogehoge


__all__ = ['MitakalabFormatter']


_escape_html_table = {
	ord('&'): u'&amp;',
	ord('<'): u'&lt;',
	ord('>'): u'&gt;',
	ord('"'): u'&quot;',
	ord("'"): u'&#39;',
	}

def escape_html(text, table=_escape_html_table):
	"""Escape &, <, > as well as single and double quotes for HTML."""
	return text.translate(table)


def _get_ttype_class(ttype):
	fname = STANDARD_TYPES.get(ttype)
	if fname:
		return fname
	aname = ''
	while fname is None:
		aname = '-' + ttype[-1] + aname
		ttype = ttype.parent
		fname = STANDARD_TYPES.get(ttype)
	return fname + aname
	

class MitakalabFormatter(Formatter):
	r"""
	MitakaLab specific formatter for HTML output.
	
	Additional options accepted:
	
	`show_line_numbers`
	Determines whether the line number column should be shown (default:
	``True``).
	
	`first_line_number`
	The line number for the first line (default: ``1``).
	"""
	
	name = 'MitakaLab'
	aliases = ['mitakalab']
	filenames = []
	
	def __init__(self, **options):
		Formatter.__init__(self, **options)
		self.show_line_numbers = get_bool_opt(options, 'show_line_numbers', True)
		self.first_line_number = abs(get_int_opt(options, 'first_line_number', 1))
		self.highlight_lines = get_list_opt(options, 'highlight_lines', []) # hogehoge
		self.file_name = options.get('filename', '') # hogehoge
		
	def _wrap_table(self, inner):
		"""
		Wrap the whole thing into a table and add line numbers
		"""
		dummyoutfile = StringIO.StringIO()
		lncount = 0
		for line in inner:
			lncount += 1
			dummyoutfile.write(line)
				
		sln = self.show_line_numbers
		if sln:
			fl = self.first_line_number
			hl = self.highlight_lines # hogehoge
			fn = self.file_name # hogehoge
			mw = len(str(lncount + fl - 1))
					
			points = []
			lines = []
			for i in range(fl, fl+lncount):
				# hogehoge
				# points.append('<span id="P-%s-%d" rel="P-%s-%d" class="point">' % (fn, i, fn, i) + '-</span>')
				# hogehoge
				if i in hl:
					lines.append('<span id="L%d-%s" rel="L%d" class="number highlight_number" data-lineno="%d" data-filename="%s">' % (i, fn, i, i, fn) + '%*d' % (mw, i) + '</span>')
				else:
					lines.append('<span id="L%d-%s" rel="L%d" class="number" data-lineno="%d" data-filename="%s">' % (i, fn, i, i, fn) + '%*d' % (mw, i) + '</span>')

			lp = '\n'.join(points)
			ls = '\n'.join(lines)

			yield '<table class="lines highlight"><tr>'
			# yield '<td class="line_points">' + lp + '</td>'
			yield '<td class="line_numbers">' + ls + '</td>'
			yield '<td class="line_data">'
			yield dummyoutfile.getvalue()
			yield '</td></tr></table>'

	def _wrap_code_lines(self, inner):
		"""
		Wrap each line in a <div class="line">
		"""
		# subtract 1 since we have to increment i *before* yielding
		i = self.first_line_number - 1
		hl = self.highlight_lines
		fn = self.file_name	

		for line in inner:
			i += 1
			# hogehoge
			if i in hl:
				yield '<pre class="highlight_line"><div id="C%d-%s" class="line" data-lineno="%d" data-filename="%s">%s</div></pre>' % (i, fn, i, fn, line)
			else:
				yield '<pre><div id="C%d-%s" class="line" data-lineno="%d" data-filename="%s">%s</div></pre>' % (i, fn, i, fn, line)

	def _format_code_lines(self, tokensource):
		"""
		Just format the tokens, without any wrapping tags.
		Yield individual lines.
		"""
		# for <span style=""> lookup only
		escape_table = _escape_html_table
			
		lspan = ''
		line = ''
		for ttype, value in tokensource:
			cls = _get_ttype_class(ttype)
			cspan = cls and '<span class="%s">' % cls or ''
			
			parts = escape_html(value).split('\n')

			# for all but the last line
			for part in parts[:-1]:
				if line:
					if lspan != cspan:
						line += (lspan and '</span>') + cspan + part + \
								(cspan and '</span>')
					else: # both are the same
						line += part + (lspan and '</span>')
					yield line
					line = ''
				elif part:
					yield cspan + part + (cspan and '</span>')
				else:
					yield '<br/>'
			# for the last line
			if line and parts[-1]:
				if lspan != cspan:
					line += (lspan and '</span>') + cspan + parts[-1]
					lspan = cspan
				else:
					line += parts[-1]
			elif parts[-1]:
				line = cspan + parts[-1]
				lspan = cspan
			# else we neither have to open a new span nor set lspan

		if line:
			yield line + (lspan and '</span>')

	def format_unencoded(self, tokensource, outfile):
		"""
		The formatting process uses several nested generators; which of
		them are used is determined by the user's options.
		
		Each generator should take at least one argument, ``inner``,
		and wrap the pieces of text generated by this.
		"""
		source = self._format_code_lines(tokensource)
		source = self._wrap_code_lines(source)
		source = self._wrap_table(source)
		
		for piece in source:
			outfile.write(piece)
				
