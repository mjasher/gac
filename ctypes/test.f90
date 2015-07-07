function prnt(s)          ! byref(s), byval(length) [long int, implicit]
!    character(len=*):: s  ! variable length input
    CHARACTER s*(*)

    logical :: prnt
    write(*, "(A)") s     ! formatted, to remove initial space
    prnt = .true.
end function prnt

function sin_2(r)         ! byref(r)
    real:: r, sin_2       ! float; use real(8) for double
    sin_2 = sin(r)**2
end function sin_2


      SUBROUTINE QREF(A,TOTAL, Z, Y, X)
      INTEGER Z
      INTEGER Y
      INTEGER X
      REAL,  DIMENSION(Z, Y, X) ::A
      REAL TOTAL

      WRITE(*,*) A

      DO I = 1,Z
      DO J = 1,Y
      DO K = 1,X
      TOTAL = TOTAL + A(I,J,K)
      END DO
      END DO
      END DO
      END SUBROUTINE


      SUBROUTINE halfhalf(NOFLO, X, Y, Z, B, A, NAME)
      REAL NOFLO
      INTEGER X
      INTEGER Y
      INTEGER Z
      REAL(8),  DIMENSION(X, Y, Z) ::B
      INTEGER(8),  DIMENSION(X, Y, Z) ::A
      CHARACTER NAME*(*)

      WRITE(*,*) "halfhalf"
      WRITE(*,*) NOFLO
      WRITE(*,*) X, Y, Z
      WRITE(*,*) B
      WRITE(*,*) A
      WRITE(*,*) NAME

      DO I = 1,X
      DO J = 1,Y
      DO K = 1,Z
      WRITE(*,*) I,J,K,B(I,J,K)
      END DO
      END DO
      END DO

      END SUBROUTINE

