#include <iostream>
#include <fstream>
#include <cstdlib>
#include <vector>
#include <list>
#include <unordered_map>

using namespace std;

const int MINTOKENS = 2;

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
    
    if (argc != 2) {
        cerr << "Usage: ngramtest file" << endl;
        exit(2);
    }
    
    string filename = argv[1];
    cerr << "Processing " << filename << endl;
    //int n = atoi(argv[2]);
    
    
    string line;    
    unordered_map< string, int> freqlist;
    const int MAXLENGTH = 6;


    for (int n = 1; n <= MAXLENGTH; n++) {
        cerr << "Counting " << n << "-grams" << endl;
        int linenum = 0;
        int tokens = 0;
        ifstream *IN =  new ifstream( filename.c_str() );    
        while (IN->good()) {
            linenum++;
            if (linenum % 10000 == 0) {
                cerr << "\t@" << linenum << endl;
            }
            getline(*IN, line);  
            vector<string> words;
            split(line, words);
                            
            int l = words.size();        
            for (int i = 0; i < l - n + 1; i++) {
                vector<string> ngram = vector<string>(words.begin() + i, words.begin() + i + n);
            
                
                if (n > 2) {
                    vector<string> subngram1 = vector<string>(words.begin() + i, words.begin() + i + (n - 1));
                    string subngram1_s = join(subngram1);
                    if (!freqlist.count(subngram1_s)) continue;
                    
                    vector<string> subngram2 = vector<string>(words.begin() + i + 1, words.begin() + i + n - 1);
                    string subngram2_s = join(subngram2);
                    if (!freqlist.count(subngram2_s)) continue;
                }
                
                string ngram_s = join(ngram);            
                freqlist[ngram_s] += 1;
                tokens++;
                //cout << ngram_s << endl;
            

                 
            }            
            
       }
       cerr << "Found " << tokens << " " << n << "-grams" << endl;

       //prune n-grams
       int pruned = 0;
       for(unordered_map<string,int>::iterator iter = freqlist.begin(); iter != freqlist.end(); iter++ ) {
            if (iter->second <= MINTOKENS) {
                //if (iter->second != 0) pruned++;
                pruned += freqlist.erase(iter->first);
            }
       }
       cerr << "Pruned " << pruned << " " << n << "-grams, " << (tokens - pruned) <<  " left" << endl;
       
       
 
    }   

}
