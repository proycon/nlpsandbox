#include <iostream>
#include <iomanip>
#include <fstream>
#include <cstdlib>
#include <vector>
#include <list>
#include <unordered_map>
#include <utility>
#include <limits>

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

vector< pair<int,int> > get_consecutive_gaps(const int n) {
    vector< pair<int,int> > gaps;
    int begin = 1;
    while (begin < n) {
        int length = (n - 1) - begin;
        while (length > 0) {
            pair<int,int> gap = make_pair(begin, length);
            gaps.push_back(gap);
            length--;
        }
        begin++;
    }      
    return gaps;
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
    unordered_map< string, int> skipgrams;
    const int MAXLENGTH = 6;


    for (int n = 1; n <= MAXLENGTH; n++) {
        cerr << "Counting " << n << "-grams" << endl;
        int linenum = 0;
        int tokens = 0;
        int skiptokens = 0;
        const vector< pair<int,int> > gaps = get_consecutive_gaps(n);
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
            
                for (int j = 0; j < gaps.size(); j++) {
                    const int begin = gaps[j].first;  
                    const int length = gaps[j].second;
                    
                    const vector<string> skipgram_pregap = vector<string>(words.begin() + i, words.begin() + i + begin);
                    const string skipgram_pregap_s = join(skipgram_pregap);
                    
                    if (!freqlist.count(skipgram_pregap_s)) continue;

                    const vector<string> skipgram_postgap = vector<string>(words.begin() + i + begin + length, words.begin() + i + n);                    
                    const string skipgram_postgap_s = join(skipgram_postgap);
                    if (!freqlist.count(skipgram_postgap_s)) continue;
                    
                    const string skipgram = skipgram_pregap_s + " | " + skipgram_postgap_s;
                    skipgrams[skipgram] += 1;
                    skiptokens++;
                    
                }
                
                 
            }            
            
       }
       cerr << "Found " << tokens << " " << n << "-grams and " << skiptokens << " skipgrams" << endl;

       //prune n-grams
       int pruned = 0;
       int ngramtotal = 0;
       for(unordered_map<string,int>::iterator iter = freqlist.begin(); iter != freqlist.end(); iter++ ) {
            if (iter->second <= MINTOKENS) {
                pruned += freqlist.erase(iter->first);
            } else {
                ngramtotal += iter->second;
            }
       }
       cerr << "Pruned " << pruned << " " << n << "-grams, " << (tokens - pruned) <<  " left" << endl;
       
       //prune skipgrams
       pruned = 0;
       int skipgramtotal = 0;
       for(unordered_map<string,int>::iterator iter = skipgrams.begin(); iter != skipgrams.end(); iter++ ) {
            if (iter->second <= MINTOKENS) {
                pruned += skipgrams.erase(iter->first);
            } else {
                skipgramtotal += iter->second;
            }
       }
       cerr << "Pruned " << pruned << " " << "skipgrams, " << (skiptokens - pruned) <<  " left" << endl;
       
       
       for(unordered_map<string,int>::iterator iter = freqlist.begin(); iter != freqlist.end(); iter++ ) {
           const double freq = (double) iter->second / ngramtotal;
           cout <<  setprecision(numeric_limits<double>::digits10 + 1) <<  iter->first << '\t' << iter->second << '\t' << freq << endl;
       }
       
       for(unordered_map<string,int>::iterator iter = skipgrams.begin(); iter != skipgrams.end(); iter++ ) {
           const double freq = (double) iter->second / skipgramtotal;
           cout <<  setprecision(numeric_limits<double>::digits10 + 1) << iter->first << '\t' << iter->second << '\t' << freq << endl;
       }       
 
    }   

}
