#include <iostream>
#include <iomanip>
#include <fstream>
#include <cstdlib>
#include <vector>
#include <list>
#include <unordered_map>
#include <utility>
#include <limits>
#include <cmath>

using namespace std;
const int MINTOKENS = 2;




using namespace std;


unsigned int bytestoint(unsigned char* a, const int l) {
    int result = 0;
    for (int i = 0; i < l+1; i++) {
        result += *(a + i) * pow(256,i);
    }
    return result;
}

    

class ClassDecoder {
    private:
     unordered_map<unsigned int,string> classes;
    public:
    
    ClassDecoder(const string filename);
    
    vector<string> decodeseq(vector<int> seq);
    
    void decodefile(const string filename);
    
    int size() {
        return classes.size();
    }
    
    string operator[](unsigned int key) {
         return classes[key];
    }
};

ClassDecoder::ClassDecoder(const string filename) {
       ifstream *IN =  new ifstream( filename.c_str() );    

        while (IN->good()) {
          string line;
          getline(*IN, line);              
          for (int i = 0; i < line.size(); i++) {
              if (line[i] == '\t') {
                  const string cls_s = string(line.begin(), line.begin() + i);
                  unsigned int cls = (unsigned int) atoi(cls_s.c_str());
                  const string word = string(line.begin() + i + 1, line.end());
                  classes[cls] = word;
                  //cerr << "CLASS=" << cls << " WORD=" << word << endl;
              }
              
          }
        }
        IN->close();  
}

        
vector<string> ClassDecoder::decodeseq(vector<int> seq) {
    vector<string> result;
    const int l = seq.size();
    for (int i; i < l; i++) 
        result.push_back( classes[seq[i]] ); 
    return result;
}



void ClassDecoder::decodefile(const string filename) {
    ifstream *IN = new ifstream(filename.c_str()); //, ios::in | ios::binary);
    unsigned char buffer[10];
    int n = 0;
    while (IN->good()) {
        char bufchar;
        IN->get(bufchar);
        
        unsigned char c = (unsigned char) bufchar;
        buffer[n] = c;
        //cout << "READ: " << ((int) c) << endl;
        if (c == 0) {
            //cout << "N: " << n << endl;
            const unsigned int cls = bytestoint(buffer, n - 1);  
            if (cls == 1) {
                cout << endl;
            } else {
                //cout << cls << ' ';
                cout << classes[cls] << ' ';
            }
            n = 0;
        } else {
            n++;
        }
    }
    IN->close();                    
} 



int readline(istream* IN, unsigned char* buffer) {
    int n = 0;
    short eolsequence = 0; //3 stages: 0 1 0 , when all three are found, we have a sentence
    while (IN->good()) {
        char bufchar;
        IN->get(bufchar);
        unsigned char c = (unsigned char) bufchar;
        buffer[n] = c;        
        if (c == 0) {
            eolsequence++;
            if (eolsequence == 3) return n - 3; //minus last three 0 1 0 bytes            
        } else if (c == 1) {
            if (eolsequence == 1) {
                eolsequence++;
            } else {
                eolsequence = 0
            }
        } else {
            eolsequence = 0;
        }
    }    
    return 0;
}



class EncNGram {
    public:
     unsigned char* data;
     char size;
    
     EncNGram(unsigned char* dataref, char size) {
       //create a copy of the character data (will take less space than storing pointers anyhow!)
       this->size = size;
       data = new unsigned char[size];
       n = 1;
       for (int i = 0; i < size; i++) {
            data[i] = dataref[i];
            if data[i] = dataref[i]
       }        
     }
     ~EncNGram() {
         free(data);
     }
     
     const int n() {
        int count = 1; 
        for (int i = 0; i < size; i++) {
            if (data[i] == 0) count++;
        }    
        return count;
     }
     
     string decode(ClassDecoder& classdecoder) {
        string result = ""; 
        for (int i = 0; i < size; i++) {
            if (c == 0) {
                //cout << "N: " << n << endl;
                const unsigned int cls = bytestoint(data, i - 1);  
                if (cls == 1) {
                    return line;
                } else {
                    result += classdecoder[cls];
                }
                n = 0;
            } else {
                n++;  
            }
        }
    }
    
    EncNGram slice(const int begin,const int length) {
        
    }
};


template <>
struct std::tr1::hash<EncNGram> {
 public: 
        size_t operator()(EncNGram ngram) const throw() {
            //jenkins hash: http://en.wikipedia.org/wiki/Jenkins_hash_function
            unsigned long h, i;
            for(h = i = 0; i < ngram.size; ++i)
            {
                h += ngram.data[i];
                h += (h << 10);
                h ^= (h >> 6);
            }
            h += (h << 3);
            h ^= (h >> 11);
            h += (h << 15);
            return h;
        }
};

typedef unordered_map<EncNGram,int> freqlist;

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


EncNGram getngram(int index, int n, unsigned char *line, int size) {
    int currentindex = 0;
    int beginpos = -1;
    int endpos = -1;
    for (int i = 0; i < size; i++) {
        if (line[i] == 0) {
            currentindex++;
            if (currentindex == index) {
                beginpos = i+1;
            } else if (currentindex == index + n) {
                endpos = i - 1;
            }
        }        
    }
    if (endpos == -1) {
        endpos = size - 1;
    }
    const char size = (char) (endpos - beginpos + 1);
    return EncNGram(line + pos, size); 
}

int main( int argc, char *argv[] ) {
    
    if (argc != 2) {
        cerr << "Usage: ngramtest classfile encoded-corpus" << endl;
        exit(2);
    }
    
    const string classfile = argv[1];
    
    ClassDecoder classdecoder = ClassDecoder(classfile);
    
    string corpusfile = argv[2];
    
    
    
    
    
    
    cerr << "Processing " << filename << endl;
    //int n = atoi(argv[2]);
    
    
    unsigned char* line[1024];    
    vector<freqlist*> ngrams;
    vector<freqlist*> skipgrams;
    const int MAXLENGTH = 6;
    
    int[MAXLENGTH+1] tokencount;
    


    for (int n = 1; n <= MAXLENGTH; n++) {
        cerr << "Counting " << n << "-grams" << endl;
        (*ngrams)[n] = new freqlist();
        freqlist ngramfreqlist = (*ngrams)[n];
        
        
        int linenum = 0;
        tokencount[n] = 0;
        int skiptokens = 0;
        const vector< pair<int,int> > gaps = get_consecutive_gaps(n);
        ifstream *IN =  new ifstream( filename.c_str() );    
        vector<unsigned int> words;
        while (IN->good()) {
            const int linesize = readline(IN, line);
            if (linesize == 0) break;
                    
            linenum++;
            if (linenum % 10000 == 0) {
                cerr << "\t@" << linenum << endl;
            }
                            
            const int l = words.size();        
            for (int i = 0; i < l - n + 1; i++) {
                EncNGram ngram = getngram(i,n), line, linesize;
                if (ngram.n > 2)
                    EncNGram subngram1 = ngram.slice(0, ngram.n - 1);
                    if (!(*ngrams)[n].count(subngram1)) continue; //if subngram does not exist (count==0), no need to count ngram, skip to next
                    
                                         
                    EncNGram subngram2 = ngram.slice(1, ngram.n - 1);
                    if (!(*ngrams)[n].count(subngram2)) continue; //if subngram does not exist (count==0), no need to count ngram, skip to next
                                        
                }
                                    
                (*ngrams)[n][ngram] += 1;
                tokencount[n]++;
                //cout << ngram_s << endl;
            
                for (int j = 0; j < gaps.size(); j++) {
                    const int begin = gaps[j].first;  
                    const int length = gaps[j].second;
                    
                    
                    
                    const vector<string> skipgram_pregap = vector<string>(words.begin() + i, words.begin() + i + begin);
                    const string skipgram_pregap_s = join(skipgram_pregap);
                    
                    if (!(*ngrams).count(skipgram_pregap_s)) continue;

                    const vector<string> skipgram_postgap = vector<string>(words.begin() + i + begin + length, words.begin() + i + n);                    
                    const string skipgram_postgap_s = join(skipgram_postgap);
                    if (!(*ngrams)[n].count(skipgram_postgap_s)) continue;
                    
                    const string skipgram = skipgram_pregap_s + " | " + skipgram_postgap_s;
                    skipgrams[skipgram] += 1;
                    skiptokens++;
                    
                }
                
                 
            }            
            
        };

       cerr << "Found " << tokens << " " << n << "-grams and " << skiptokens << " skipgrams" << endl;

       //prune n-grams
       int pruned = 0;
       int ngramtotal = 0;
       for(unordered_map<string,int>::iterator iter = ngrams.begin(); iter != ngrams.end(); iter++ ) {
            if (iter->second <= MINTOKENS) {
                pruned += ngrams.erase(iter->first);
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
       
       
       for(unordered_map<string,int>::iterator iter = ngrams.begin(); iter != ngrams.end(); iter++ ) {
           const double freq = (double) iter->second / ngramtotal;
           cout <<  setprecision(numeric_limits<double>::digits10 + 1) <<  iter->first << '\t' << iter->second << '\t' << freq << endl;
       }
       
       for(unordered_map<string,int>::iterator iter = skipgrams.begin(); iter != skipgrams.end(); iter++ ) {
           const double freq = (double) iter->second / skipgramtotal;
           cout <<  setprecision(numeric_limits<double>::digits10 + 1) << iter->first << '\t' << iter->second << '\t' << freq << endl;
       }       
 
    }   

}
