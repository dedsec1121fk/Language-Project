program language_worker
  use iso_fortran_env, only: output_unit
  implicit none
  integer, parameter :: key = int(z'67')
  character(len=1048576) :: line
  character(len=1048576) :: h
  character(len=1048576) :: out
  character(len=2) :: pair
  integer :: ios, n, i, v, pos
  do
    read(*,'(A)',iostat=ios) line
    if (ios /= 0) exit
    line = trim(line)
    if (line == 'PING') then
      write(*,'(A)') 'PONG'; flush(output_unit); cycle
    end if
    if (line == 'QUIT') exit
    n = len_trim(line)
    if (n >= 2 .and. (line(1:1) == 'E' .or. line(1:1) == 'D') .and. line(2:2) == ' ') then
      h = line(3:n); out=''; pos=1
      do i=1,len_trim(h),2
        pair=h(i:i+1); read(pair,'(Z2)',iostat=ios) v
        if (ios /= 0) exit
        v=ieor(v,key); write(out(pos:pos+1),'(Z2.2)') v; pos=pos+2
      end do
      if (ios == 0) then
        write(*,'(A)') out(1:max(0,pos-1)); flush(output_unit)
      else
        write(*,'(A)') 'ERR'; flush(output_unit)
      end if
    else
      write(*,'(A)') 'ERR'; flush(output_unit)
    end if
  end do
end program language_worker
