from parse import parse
from dateutil.parser import parse as parse_datetime
import subprocess, pickle, argparse, os, json, datetime, sys, pprint

def jsonconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def find_gitrepos(initial_path):

    repos = []
    for name in os.listdir(initial_path):
        path = os.path.join(initial_path, name)
        if os.path.isdir(path):
            repos.append(path)
            command = ["git","submodule", "foreach", "--recursive"]
            p = subprocess.Popen(command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                cwd=path)
            output, _ = p.communicate()
            output    = output.decode()
            for line in output.split('\n'):
                res = parse("Entering '{}'", line)
                if res:
                    repo = res.fixed[0]
                    repos.append( os.path.join(path, repo) )
            
    return repos
        



def gitstats_per_user(path, recursive=False, since=None, until=None, authors_emails={}, use_paths=None, filterby_emails=None ):
    """
    :param str path: Path to analyse. 
                     If the recursive is false, 
                     it should be the path o a repository.
                     If the recursive is true, 
                     it should be the parent path of several repositories
    :param bool recursive: Indicate if it should read the stats from the path directory
                           or the subdirectories in the path.    
    
    :return:
        A dictionary with the format
        {
            'author': [{'date':..., 'files updated':..., 'insertions':..., 'deletions':...}],
            ...
        }
    """
    if use_paths is None:
        directories = [path] if not recursive else find_gitrepos(path)
    else:
        directories = use_paths

    authors = {}
    emails  = {}
    for directory in directories:
        print(directory)

        command = ["git","log","--shortstat","--all"]
        if since: command += ['--since', since.strftime('%Y.%m.%d')]
        if until: command += ['--until', until.strftime('%Y.%m.%d')]
        
        p = subprocess.Popen(command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            cwd=directory)
        output, _ = p.communicate()
        output    = output.decode()

        for commit in output.split('commit ')[1:]:
            lines = commit.split('\n')

            deletions     = 0
            insertions    = 0
            files_changed = 0
            
            for row in lines:
                
                if row.startswith('Author:'):
                    author = row[8:]
                    author = parse("{} <{}>", author)
                    author, email = author.fixed 
                    emails[author] = email
                    if email in authors_emails:
                        author = authors_emails[email]
                elif row.startswith('Date:'):
                    date   = parse_datetime(row[8:])
                elif ' changed' in row:
                    data = row.strip().split(',')
                    for v in data:
                        v = v.strip()
                        
                        res = parse("{:d} deletions(-)", v)
                        if res:
                            deletions = res.fixed[0]
                        else:
                            res = parse("{:d} deletion(-)", v)
                            if res:
                                deletions = res.fixed[0]

                        res = parse("{:d} files changed", v)
                        if res:
                            files_changed = res.fixed[0]
                        else:
                            res = parse("{:d} file changed", v)
                            if res:
                                files_changed = res.fixed[0]

                        res = parse("{:d} insertions(+)", v)
                        if res:
                            insertions = res.fixed[0]
                        else:
                            res = parse("{:d} insertion(+)", v)
                            if res:
                                insertions = res.fixed[0]
                    
            if filterby_emails and email not in filterby_emails:
                continue
                
            if author not in authors: authors[author] = []
            
            authors[author].append({
                'date': date, 
                'files changed': files_changed, 
                'deletions': deletions, 
                'insertions': insertions
            })

        for author, commits in authors.items():
            authors[author] = sorted(commits, key=lambda x: x['date'])

    return authors, directories, emails


def main():
    parser = argparse.ArgumentParser(description='git-stats generate stats per user of git repositories.')
    parser.add_argument('-r', action='store_true', dest='recursive', help='Check all the repositories in the subfolders')
    parser.add_argument('--path', default='.', type=str, help='Path to check')
    parser.add_argument('--format', type=str, help='Output format')
    args = parser.parse_args()

    data, _, _ = gitstats_per_user(args.path, args.recursive)

    if args.format=='json':
        sys.stdout.write(json.dumps(data, default=jsonconverter))
    else:
        pp = pprint.PrettyPrinter(indent=2, width=120)
        pp.pprint(data)

if __name__=='__main__':
    main()
    