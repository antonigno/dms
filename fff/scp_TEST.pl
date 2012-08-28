#!/usr/bin/perl

$path = "/home/duff/controlli_xml";

opendir(DIR, $path) or die "$!";

@files = grep /xml/, readdir(DIR);
foreach $file (@files){
    print "$file\n";
    $cmd = "scp -o ConnectTimeout=5 -i /home/duff/legnux_key $path/$file god\@10.41.9.26:/tmp";
    system("$cmd");
}
