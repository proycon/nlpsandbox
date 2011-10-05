#include <iostream>
#include <fstream>
#include <cstdlib>
#include <vector>
#include <list>
#include <unordered_map>

using namespace std;


int split(string str, vector<string> &result, char delim = ' ') {
  string tmp = "";
  string::iterator i;
  result.clear();

  for (i = str.begin(); i <= str.end(); ++i) {
    if((const char)*i != delim  && i != str.end()) {
      tmp += *i;
    } else {
      if (!tmp.empty()) result.push_back(tmp);
      tmp = "";
    }
  }
  return result.size();
}

string join(vector<string> seq, char delim = ' ') {
    const int l = seq.size();
    
    //compute size
    int N = l - 1; //number of spaces
    for (int i = 0; i < l; i++) N += seq[i].size();
    
    char s[N];
    int cursor = 0;
    for (int i = 0; i < l; i++) {
        const int wordlength = seq[i].size();
        for (int j = 0; j < wordlength; j++) {
            s[cursor++] = seq[i][j];
        }
        if (i < l - 1) s[cursor++] = ' ';
    }
    s[cursor] = '\0';
    return s;
}


int main( int argc, char *argv[] ) {
    
    if (argc != 3) {
        cerr << "Usage: ngramtest file n" << endl;
        exit(2);
    }
    
    string filename = argv[1];
    cerr << "Processing " << filename << endl;
    int n = atoi(argv[2]);
    
    
    ifstream *IN =  new ifstream( filename.c_str() );    
    string line;    
    unordered_map< string, int> freqlist;
    const int MAXLENGTH = 6;

    for (int n = 1; n <= MAXLENGTH; n++) {
        cerr << "Counting " << n << "-grams" << endl;

        IN->seekg(0);
        while (IN->good()) {
            getline(*IN, line);  
            vector<string> words;
            split(line, words);
            
                
            int l = words.size();        
            for (int i = 0; i < l - n + 1; i++) {
                vector<string> ngram = vector<string>(words.begin() + i, words.begin() + i + n);
                
                
                string ngram_s = join(ngram);            
                //cout << ngram_s << endl;
                freqlist[ngram_s] += 1;
                
            }            
            
       } 
    }   

}
