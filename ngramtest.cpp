#include <iostream>
#include <fstream>
#include <cstdlib>
#include <vector>

using namespace std;

void split(string str, vector<string> &result, char delim = ' ') {
  string tmp;
  string::iterator i;
  result.clear();

  for(i = str.begin(); i <= str.end(); ++i) {
    if((const char)*i != delim  && i != str.end()) {
      tmp += *i;
    } else {
      result.push_back(tmp);
      tmp = "";
    }
  }
}



int main( int argc, char *argv[] ){
    
    if (argc != 3) {
        cerr << "Usage: ngramtest file n" << endl;
        exit(2);
    }
    
    string filename = argv[1];
    cerr << "Processing " << filename << endl;
    int n = atoi(argv[2]);
    
    
    ifstream *IN =  new ifstream( filename.c_str() );
    
    string line;    
    while (IN->good()) {
        getline(*IN, line);  
        vector<string> words;
        split(line, words);
        
        int l = words.size();        
        for (int i = 0; i < l - n + 1; i++) {
            vector<string> ngram = vector<string>(words.begin() + i, words.begin() + i + n);
            
            for (int j = 0; j < ngram.size(); j++) {
                if (j > 0) cout << " ";
                cout << ngram[j];                
            }
            cout << endl;
        }
    }   

}
