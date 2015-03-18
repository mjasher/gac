      SUBROUTINE QREF(A,TOTAL)
      INTEGER A(4,3), TOTAL
      DO I = 1,4
      DO J = 1,3
      TOTAL = TOTAL + A(I,J)
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