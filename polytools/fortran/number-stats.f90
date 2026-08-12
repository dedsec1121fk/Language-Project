program number_stats
implicit none
integer :: narg,ios,n
character(len=4096) :: path
real(8) :: x,s,mn,mx
narg=command_argument_count()
if(narg<1)then;print *,'Usage: number-stats FILE  ! one numeric record per line';stop 2;endif
call get_command_argument(1,path)
if(trim(path)=='--help')then;print *,'Usage: number-stats FILE  ! one numeric record per line';stop;endif
open(unit=10,file=trim(path),status='old',action='read',iostat=ios);if(ios/=0)stop 2
n=0;s=0d0;mn=huge(1d0);mx=-huge(1d0)
do
 read(10,*,iostat=ios)x
 if(ios<0)exit
 if(ios>0)then;cycle;endif
 n=n+1;s=s+x;if(x<mn)mn=x;if(x>mx)mx=x
enddo
close(10)
print '(A,I0)','count=',n
if(n>0)then;print '(A,ES24.16)','min=',mn;print '(A,ES24.16)','max=',mx;print '(A,ES24.16)','mean=',s/dble(n);endif
end program
