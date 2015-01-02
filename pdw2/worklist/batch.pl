#!/usr/bin/perl -w


open G, ">list.csv" or die "can't open list.csv $!";

for $n (1..477) {
	my $file = "page$n";
	open F, $file or die "can't open $file $!";

	while(<F>)  {
		($rdf, $title) = $_ =~ m/<a href="([^"]+)" ><span class="titre">([^<]+)/;
		($author) = $_ =~ m/<span class="auteur">([^<]+)/;
		if($rdf && $title) { print G "$author\t$title\t$rdf \n"; }
	}

	close F; 

}

close G;
