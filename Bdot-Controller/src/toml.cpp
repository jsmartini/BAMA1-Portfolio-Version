#include "toml.h"
#include <iostream>

using namespace std;


int main(int argc, char* argv[])
{

    toml::ParseResult pr = toml::parseFile(argv[1]);

    const toml::Value& cfg = pr.value;
    if (!pr.valid()) 
    {
        cout << pr.errorReason << endl;
        return 0;
    }
    

}