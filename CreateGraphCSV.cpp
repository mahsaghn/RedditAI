#include<iostream>
#include<fstream>
#include<string>
#include<vector>
#include<map>
#include<sstream>

using namespace std;

map<string, vector<string>> subreddits;
map<string, int> type;
map<string, int> programmer;
vector<string> users;

int main()
{
	ifstream file("raw_graph.txt");
    string line;

    while (getline(file, line)) {          // read each line
        stringstream ss(line);
        string value;
        vector<std::string> row;

        while (getline(ss, value, ',')) {  // split by comma
            row.push_back(value);
        }

        string user = row[0];
		type[user] = stoi(row[1]);
		programmer[user] = stoi(row[2]);
		for (size_t i = 3; i < row.size(); ++i) 
			subreddits[user].push_back(row[i]);
		users.push_back(user);
		
    }
	ofstream outfile("nodes.csv");
	outfile << "Id,Label,Type,Programmer\n";
	for (const auto& user : users) 
	{
		outfile << user << "," << user << "," << type[user] <<","<< programmer[user] << "\n";
	}
	outfile.close();

	ofstream edgefile("edges.csv");
	edgefile << "Source,Target,Weight\n";
	for (int i = 0; i < users.size(); ++i)
	{
		cout << i << '\n';
		string user1 = users[i];
		for (int j = i + 1; j < users.size(); ++j)
		{
			string user2 = users[j];
			int common = 0;
			for (const auto& sub : subreddits[user1])
			{
				for (const auto& sub2 : subreddits[user2])
				{
					if (sub == sub2)
					{
						common++;
						break;
					}
				}
			}
			if (common > 0)
			{
				edgefile << user1 << "," << user2 << "," << common << "\n";
			}
		}
	}
	edgefile.close();
    return 0;
}