# delete extra paths in fat tree topology
BEGIN{
	noprint = 0
	count = 0
}
{
	if ($4 > 32 || $5 > 32)
	{
		noprint = 0; 
	}
	else{
		if ($4 % 4 == 1 && $5 - $4 <4)
		{
			if (count < 4)
			{
				noprint = 1;
				#print "intra " count " " $4 " " $5 " " $0;
				print $0
				count ++;
			}
			else
			{
				count ++;
				if (count == 16)
				{
					count = 0;
				}
			}
		}
		else if ($4 % 4 == 2 && $5 - $4 <3)
		{
			if (count < 4)
			{
				noprint = 1;
				#print "intra " count " " $4 " " $5 " " $0;
				print $0
				count ++;
			}
			else
			{
				count ++;
				if (count == 16)
				{
					count = 0;
				}
			}
		}
		else if ($4 % 4 == 3 && $5 - $4 <2)
		{
			if (count < 4)
			{
				noprint = 1;
				#print "intra " count " " $4 " " $5 " " $0;
				print $0
				count ++;
			}
			else
			{
				count ++;
				if (count == 16)
				{
					count = 0;
				}
			}
		}
		else
		{
			noprint = 1;
			#print "inter " $4 " " $5 " " $0;
			print $0
		}
	}
	
}