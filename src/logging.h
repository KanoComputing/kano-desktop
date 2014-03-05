//
// Macro to log in debug mode. When built for release, the code just disappears.
//
// Copyright (C) 2013-2014 Kano Computing Ltd.
// License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
//
// An app to show and bring life to Kano-Make Desktop Icons.
//

#include <iostream>

using namespace std;

#ifdef DEBUG
#define log(s)        { cout << __FILE__ << ":" << __FUNCTION__ << "()@" << __LINE__ << " => " << s << endl ;}
#define log1(s,f)     { cout << __FILE__ << ":" << __FUNCTION__ << "()@" << __LINE__ << " => " << s <<  " " << f \
			     << endl ;}
#define log2(s,f,j)   { cout << __FILE__ << ":" << __FUNCTION__ << "()@" << __LINE__ << " => " << s <<  " " << f \
			     << " " << j << endl ;}

#define log3(s,f,j,k) { cout << __FILE__ << ":" << __FUNCTION__ << "()@" << __LINE__ << " => " << s <<  " " << f \
			     << " " << j << " " << k << endl ;}

#define log4(s,f,j,k,l) { cout << __FILE__ << ":" << __FUNCTION__ << "()@" << __LINE__ << " => " << s <<  " " \
			       << f << " " << j << " " << k << " " << l << endl ;}

#define log5(s,f,j,k,l,m) { cout << __FILE__ << ":" << __FUNCTION__ << "()@" << __LINE__ << " => " << s <<  " " \
				 << f << " " << j << " " << k << " " << l << " " << m << endl ;}
#else
#define log(s)            {}
#define log1(s,f)         {}
#define log2(s,f,j)       {}
#define log3(s,f,j,k)     {}
#define log4(s,f,j,k,l)   {}
#define log5(s,f,j,k,l,m) {}
#endif
