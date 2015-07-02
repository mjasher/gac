      SUBROUTINE QREF(A,TOTAL, Z, Y, X)
C     INTEGER A(4,3,1), TOTAL
      INTEGER Z
      INTEGER Y
      INTEGER X
      INTEGER,  DIMENSION(Z, Y, X) ::A
C      INTEGER, DIMENSION(:,:,:), POINTER ::A
      INTEGER TOTAL
C      ALLOCATE (A(4,3,1))

      WRITE(*,*) A

      DO I = 1,Z
      DO J = 1,Y
      DO K = 1,X
      TOTAL = TOTAL + A(I,J,K)
      END DO
      END DO
      END DO
      END SUBROUTINE

      SUBROUTINE VECREF( V, TOTAL)
      INTEGER I, TOTAL, V(9)
      TOTAL = 0
      DO I = 1,9
      TOTAL = TOTAL + V(I)
      END DO
      END SUBROUTINE

      SUBROUTINE CSTRNG(S, B)
      CHARACTER*7 S
      INTEGER B
      WRITE(*,*) S, B
      END SUBROUTINE